# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import getpass
import gevent
import os
import string
import time
import tabulate
import uuid
import re
import itertools
import traceback
from functools import wraps
import logging
import datetime
import enum
import copy
from tempfile import gettempdir
from pathlib import Path
from typing import Optional, Union

from bliss import is_bliss_shell, current_session
from bliss.config.wardrobe import ParametersWardrobe
from bliss.config.conductor.client import get_redis_proxy
from bliss.scanning.writer import get_writer_class
from bliss.common.proxy import Proxy as OrigProxy
from bliss.common import logtools
from bliss.icat.client import icat_client_config
from bliss.icat.client import icat_client_from_config
from bliss.icat.client import is_null_client
from bliss.icat.client import DatasetId
from bliss.config.static import get_config
from bliss.config.settings import scan as scan_redis
from bliss.common.utils import autocomplete_property
from bliss.icat.proposal import Proposal
from bliss.icat.dataset_collection import DatasetCollection
from bliss.icat.dataset import Dataset
from bliss.icat.json_policy import RedisJsonTree
from bliss.flint.client.proxy import restart_flint

lock = gevent.lock.BoundedSemaphore()

Proxy = copy.deepcopy(OrigProxy)
del Proxy.__call__


class ScanSavingProxy(Proxy):
    def __init__(self):
        super().__init__(lambda: None, init_once=True)

    def _init(self, new_cls, *args):
        try:
            object.__delattr__(self, "__target__")
        except AttributeError:
            pass
        object.__setattr__(self, "__scan_saving_class__", new_cls)
        object.__setattr__(self, "__factory__", lambda: new_cls(*args))

    @property
    def __class__(self):
        return self.__scan_saving_class__


def ScanSaving(*args, **kwargs):
    scan_saving = current_session.scan_saving
    return scan_saving.__class__(*args, **kwargs)


class ESRFDataPolicyEvent(enum.Enum):
    Enable = "enabled"
    Disable = "disabled"
    Change = "changed"


logger = logging.getLogger(__name__)


class MissingParameter(ValueError):
    pass


class CircularReference(ValueError):
    pass


def with_eval_dict(method):
    """This passes a dictionary as named argument `eval_dict` to the method
    when it is not passed by the caller. This dictionary is used for caching
    parameter evaluations (user attributes and properties) in `EvalParametersWardrobe`.

    :param callable method: unbound method of `EvalParametersWardrobe`
    :returns callable:
    """

    @wraps(method)
    def eval_func(self, *args, **kwargs):
        # Create a cache dictionary if not provided by caller
        if "eval_dict" in kwargs:
            eval_dict = kwargs.get("eval_dict")
        else:
            eval_dict = None
        if eval_dict is None:
            logger.debug("create eval_dict (method {})".format(repr(method.__name__)))
            # Survives only for the duration of the call
            eval_dict = kwargs["eval_dict"] = {}
        if not eval_dict:
            self._update_eval_dict(eval_dict)
            logger.debug("filled eval_dict (method {})".format(repr(method.__name__)))
        # Evaluate method (passes eval_dict)
        return method(self, *args, **kwargs)

    return eval_func


class property_with_eval_dict(autocomplete_property):
    """Combine the `with_eval_dict` and `property` decorators"""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        if fget is not None:
            name = "_eval_getter_" + fget.__name__
            fget = with_eval_dict(fget)
            fget.__name__ = name
        if fset is not None:
            name = "_eval_setter_" + fset.__name__
            fset = with_eval_dict(fset)
            fset.__name__ = name
        super().__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)


def is_circular_call(funcname):
    """Check whether a function is called recursively

    :param str funcname:
    :returns bool:
    """
    # This is good enough for our purpose
    return any(f.name == funcname for f in traceback.extract_stack())


class EvalParametersWardrobe(ParametersWardrobe):
    """A parameter value in the Wardrobe can be:

        - literal string: do nothing
        - template string: fill with other parameters (recursive)
        - callable: unbound method of this class with signature
                    `method(self)` or `method(self, eval_dict=...)`
        - other: converted to string

    Methods with the `with_eval_dict` decorator will cache the evaluation
    of these parameter values (user attributes and properties).

    Properties with the `with_eval_dict` decorator need to be called with
    `get_cached_property` or `set_cached_property` to pass the cache dictionary.
    When used as a normal property, a temporary cache dictionary is created.

    The evaluation cache is shared by recursive calls (passed as an argument).
    It is not persistant unless you pass it explicitly as an argument on the
    first call to a `with_eval_dict` decorated method.

    Parameter evaluation is done with the method `eval_template`, which can
    also be used externally to evaluate any string template that contains
    wardrobe parameter fields.
    """

    FORMATTER = string.Formatter()

    # Not in Redis (class property not used in string templates)
    NO_EVAL_PROPERTIES = set()

    def _template_named_fields(self, template):
        """Get all the named fields in a template.
        For example "a{}bc{d}efg{h}ij{:04d}k" has two named fields.

        :pram str template:
        :returns set(str):
        """
        return {
            fieldname
            for _, fieldname, _, _ in self.FORMATTER.parse(template)
            if fieldname is not None
        }

    @with_eval_dict
    def eval_template(self, template, eval_dict=None):
        """Equivalent to `template.format(**eval_dict)` with additional properties:
            - The values in `eval_dict` can be callable or template strings themselves.
            - They will be evaluated recursively and replaced in `eval_dict`.

        :param str or callable template:
        :param dict eval_dict:
        """
        eval_dict.setdefault("__evaluated__", set())

        # Evaluate callable and throw exception on empty value
        if callable(template):
            try:
                template = template(self, eval_dict=eval_dict)
            except TypeError:
                template = template(self)
            if template is None:
                raise MissingParameter("Parameters value generator returned `None`")
            if not isinstance(template, str):
                template = str(template)
        else:
            if template is None:
                raise MissingParameter
            if not isinstance(template, str):
                template = str(template)

        # Evaluate fields that have not been evaluated yet
        fields = self._template_named_fields(template)
        already_evaluated = eval_dict["__evaluated__"].copy()
        eval_dict["__evaluated__"] |= fields
        for field in fields - already_evaluated:
            value = eval_dict.get(field)
            try:
                eval_dict[field] = self.eval_template(value, eval_dict=eval_dict)
            except MissingParameter:
                if hasattr(self, field):
                    self.get_cached_property(field, eval_dict)
                if field not in eval_dict:
                    raise MissingParameter(
                        f"Parameter {repr(field)} is missing in {repr(template)}"
                    ) from None

        # Evaluate string template while avoiding circular references
        fill_dict = {}
        for field in fields:
            value = eval_dict[field]
            ffield = "{{{}}}".format(field)
            if ffield in value:
                # Stop evaluating circular reference
                # raise CircularReference("Parameter {} contains a circular reference".format(repr(field)))
                fill_dict[field] = ffield
            else:
                fill_dict[field] = value
        return template.format(**fill_dict)

    def _update_eval_dict(self, eval_dict):
        """Update the evaluation dictionary with user attributes (from Redis)
        and properties when missing.

        :param dict eval_dict:
        :returns dict:
        """
        fromredis = self.to_dict(export_properties=False)
        for k, v in fromredis.items():
            if k not in eval_dict:
                eval_dict[k] = v
        for prop in self._iter_eval_properties():
            if prop in eval_dict:
                continue
            self.get_cached_property(prop, eval_dict)

    def _iter_eval_properties(self):
        """Yield all properties that will be cached when updating the
        evaluation dictionary
        """
        for prop in self._property_attributes:
            if prop not in self.NO_EVAL_PROPERTIES:
                yield prop

    def get_cached_property(self, name, eval_dict):
        """Pass `eval_dict` to a property getter. If the property has
        already been evaluated before (meaning it is in `eval_dict`)
        then that value will be used without calling the property getter.

        :param str name: property name
        :param dict eval_dict:
        :returns any:
        """
        if name in eval_dict:
            return eval_dict[name]
        _prop = getattr(self.__class__, name)
        if isinstance(_prop, property_with_eval_dict):
            logger.debug("fget eval property " + repr(name))
            if is_circular_call(_prop.fget.__name__):
                raise CircularReference(
                    "Property {} contains a circular reference".format(repr(name))
                )
            r = _prop.fget(self, eval_dict=eval_dict)
        elif isinstance(_prop, property):
            logger.debug("fget normal property " + repr(name))
            r = _prop.fget(self)
        else:
            # Not a property
            r = getattr(self, name)
        eval_dict[name] = r
        logger.debug(f"     eval_dict[{repr(name)}] = {repr(r)}")
        return r

    def set_cached_property(self, name, value, eval_dict):
        """Pass `eval_dict` to a property setter.

        :param str name: property name
        :param any value:
        :param dict eval_dict:
        """
        _prop = getattr(self.__class__, name)
        if isinstance(_prop, property_with_eval_dict):
            logger.debug("fset eval property " + repr(name))
            if is_circular_call(_prop.fset.__name__):
                raise CircularReference(
                    "Property {} contains a circular reference".format(repr(name))
                )
            _prop.fset(self, value, eval_dict=eval_dict)
            eval_dict[name] = _prop.fget(self)
        elif isinstance(_prop, property):
            logger.debug("fset normal property " + repr(name))
            _prop.fset(self, value)
            eval_dict[name] = _prop.fget(self)
        else:
            # Not a property
            setattr(self, name, value)
            eval_dict[name] = value


class BasicScanSaving(EvalParametersWardrobe):
    """Parameterized representation of the scan data file path

        base_path/template/data_filename+file_extension

    where each part (except for the file extension) is generated
    from user attributes and properties.
    """

    # Not in Redis (class attribute)
    SLOTS = ["_session_name"]

    # In Redis
    DEFAULT_VALUES = {
        # default and not removable values
        "base_path": gettempdir() + "/scans",
        "data_filename": "data",
        "template": "{session}/",
        "images_path_relative": True,
        "images_path_template": "scan{scan_number}",
        "images_prefix": "{img_acq_device}_",
        "date_format": "%Y%m%d",
        "scan_number_format": "%04d",
        # saved properties in Redis:
        "_writer_module": "hdf5",
    }

    # Not in Redis (class property)
    # attributes implemented with python properties
    PROPERTY_ATTRIBUTES = [
        "session",
        "date",
        "user_name",
        "scan_name",
        "scan_number",
        "img_acq_device",
        "writer",
        "data_policy",
    ]

    REDIS_SETTING_PREFIX = "scan_saving"

    def __init__(self, name=None, session_name=None):
        """
        This class hold the saving structure for a session.

        This class generate the *root path* of scans and the *parent* node use
        to publish data.

        The *root path* is generate using *base path* argument as the first part
        and use the *template* argument as the final part.

        The *template* argument is basically a (python) string format use to
        generate the final part of the root_path.

        i.e: a template like "{session}/{date}" will use the session and the date attribute
        of this class.

        Attribute used in this template can also be a function with one argument
        (scan_data) which return a string.

        i.e: date argument can point to this method
             def get_date(scan_data): datetime.datetime.now().strftime("%Y/%m/%d")
             scan_data.add('date',get_date)

        The *parent* node should be use as parameters for the Scan.
        """
        if not name:
            name = str(uuid.uuid4().hex)
        self._session_name = session_name
        super().__init__(
            f"{self.REDIS_SETTING_PREFIX}:{name}",
            default_values=self.DEFAULT_VALUES,
            property_attributes=self.PROPERTY_ATTRIBUTES,
            not_removable=self.DEFAULT_VALUES.keys(),
            connection=get_redis_proxy(caching=True),
        )

    def __dir__(self):
        keys = list(self.PROPERTY_ATTRIBUTES)
        keys.extend([p for p in self.DEFAULT_VALUES if not p.startswith("_")])
        keys.extend(
            [
                "clone",
                "get",
                "get_data_info",
                "get_path",
                "get_parent_node",
                "filename",
                "root_path",
                "data_path",
                "data_fullpath",
                "images_path",
                "writer_object",
                "file_extension",
                "scan_parent_db_name",
                "newproposal",
                "newcollection",
                "newsample",
                "newdataset",
                "on_scan_run",
            ]
        )
        return keys

    def __info__(self):
        d = {}
        self._update_eval_dict(d)
        d["img_acq_device"] = "<images_* only> acquisition device name"
        info_str = super()._repr(d)
        extra = self.get_data_info(eval_dict=d)
        info_str += tabulate.tabulate(tuple(extra))
        return info_str

    @with_eval_dict
    def get_data_info(self, eval_dict=None):
        """
        :returns list:
        """
        writer = self.get_cached_property("writer_object", eval_dict)
        info_table = list()
        if not writer.saving_enabled():
            info_table.append(("NO SAVING",))
        else:
            data_file = writer.get_filename()
            data_dir = os.path.dirname(data_file)

            if os.path.exists(data_file):
                label = "exists"
            else:
                label = "does not exist"
            info_table.append((label, "filename", data_file))

            if os.path.exists(data_dir):
                label = "exists"
            else:
                label = "does not exist"
            info_table.append((label, "directory", data_dir))

        return info_table

    @property
    def scan_name(self):
        return "{scan_name}"

    @property
    def scan_number(self):
        return "{scan_number}"

    @property
    def data_policy(self):
        return "None"

    @property
    def img_acq_device(self):
        return "{img_acq_device}"

    @property
    def name(self):
        """This is the init name or a uuid"""
        return self._wardr_name.split(self.REDIS_SETTING_PREFIX + ":")[-1]

    @property
    def session(self):
        """This give the name of the current session or 'default' if no current session is defined"""
        if self._session_name is None:
            return current_session.name
        return self._session_name

    @property
    def date(self):
        return time.strftime(self.date_format)

    @property
    def user_name(self):
        return getpass.getuser()

    @property
    def writer(self):
        """
        Scan writer object.
        """
        return self._writer_module

    @writer.setter
    def writer(self, value):
        if value is not None:
            # Raise error when it doew not exist
            get_writer_class(value)
        self._writer_module = value

    def get_path(self):
        return self.root_path

    @property_with_eval_dict
    def root_path(self, eval_dict=None):
        """Directory of the scan *data file*"""
        base_path = self.get_cached_property("base_path", eval_dict)
        return self._get_root_path(base_path, eval_dict=eval_dict)

    @property_with_eval_dict
    def data_path(self, eval_dict=None):
        """Full path for the scan *data file* without the extension
        This is before the writer modifies the name (given by `self.filename`)
        """
        root_path = self.get_cached_property("root_path", eval_dict)
        return self._get_data_path(root_path, eval_dict=eval_dict)

    @property_with_eval_dict
    def data_fullpath(self, eval_dict=None):
        """Full path for the scan *data file* with the extension.
        This is before the writer modifies the name (given by `self.filename`)
        """
        data_path = self.get_cached_property("data_path", eval_dict)
        return self._get_data_fullpath(data_path, eval_dict=eval_dict)

    @with_eval_dict
    def _get_root_path(self, base_path, eval_dict=None):
        """Directory of the scan *data file*"""
        template = os.path.join(base_path, self.template)
        return os.path.abspath(self.eval_template(template, eval_dict=eval_dict))

    @with_eval_dict
    def _get_data_path(self, root_path, eval_dict=None):
        """Full path for the scan *data file* without the extension
        This is before the writer modifies the name (given by `self.filename`)
        """
        data_filename = self.get_cached_property("eval_data_filename", eval_dict)
        return os.path.join(root_path, data_filename)

    @with_eval_dict
    def _get_data_fullpath(self, data_path, eval_dict=None):
        """Full path for the scan *data file* with the extension.
        This is before the writer modifies the name (given by `self.filename`)
        """
        unknowns = self._template_named_fields(data_path)
        data_path = data_path.format(**{f: "{" + f + "}" for f in unknowns})
        return os.path.extsep.join((data_path, self.file_extension))

    @property_with_eval_dict
    def eval_data_filename(self, eval_dict=None):
        """The evaluated version of data_filename"""
        return self.eval_template(self.data_filename, eval_dict=eval_dict)

    @property_with_eval_dict
    def filename(self, eval_dict=None) -> Optional[str]:
        """Full path for the scan *data file* with the extension.
        Could be modified by the writer instance.
        """
        return self.get_cached_property("writer_object", eval_dict).get_filename()

    @property_with_eval_dict
    def images_path(self, eval_dict=None):
        """Path to be used by external devices (normally a string template)"""
        images_template = self.images_path_template
        images_prefix = self.images_prefix
        images_sub_path = self.eval_template(images_template, eval_dict=eval_dict)
        images_prefix = self.eval_template(images_prefix, eval_dict=eval_dict)
        if self.images_path_relative:
            root_path = self.get_cached_property("root_path", eval_dict)
            return os.path.join(root_path, images_sub_path, images_prefix)
        else:
            return os.path.join(images_sub_path, images_prefix)

    @with_eval_dict
    def get(self, eval_dict=None):
        """
        This method will compute all configurations needed for a new scan.
        It will return a dictionary with:
            root_path -- compute root path with *base_path* and *template* attribute
            images_path -- compute images path with *base_path* and *images_path_template* attribute
                If images_path_relative is set to True (default), the path
                template is relative to the scan path, otherwise the
                images_path_template has to be an absolute path.
            db_path_items -- information needed to create the parent node in Redis for the new scan
            writer -- a writer instance
        """
        return {
            "root_path": self.get_cached_property("root_path", eval_dict),
            "data_path": self.get_cached_property("data_path", eval_dict),
            "images_path": self.get_cached_property("images_path", eval_dict),
            "db_path_items": self.get_cached_property("_db_path_items", eval_dict),
            "writer": self.get_cached_property("writer_object", eval_dict),
        }

    @property_with_eval_dict
    def scan_parent_db_name(self, eval_dict=None):
        """The Redis name of a scan's parent node is a concatenation of session
        name and data directory (e.g. "session_name:tmp:scans")
        """
        return ":".join(self.get_cached_property("_db_path_keys", eval_dict))

    @property_with_eval_dict
    def _db_path_keys(self, eval_dict=None):
        """The Redis name of a scan's parent node is a concatenation of session
        name and data directory (e.g. ["session_name", "tmp", "scans"])

        Duplicate occurences of "session_name" are removed.

        :returns list(str):
        """
        session = self.session
        parts = self.get_cached_property("root_path", eval_dict).split(os.path.sep)
        return [session] + [p for p in parts if p and p != session]

    @property_with_eval_dict
    def _db_path_items(self, eval_dict=None):
        """For scan's parent node creation (see `get_parent_node`)

        :returns list(tuple):
        """
        parts = self.get_cached_property("_db_path_keys", eval_dict)
        types = ["container"] * len(parts)
        return list(zip(parts, types))

    @property_with_eval_dict
    def writer_object(self, eval_dict=None):
        """This instantiates the writer class

        :returns bliss.scanning.writer.File:
        """
        root_path = self.get_cached_property("root_path", eval_dict)
        images_path = self.get_cached_property("images_path", eval_dict)
        data_filename = self.get_cached_property("eval_data_filename", eval_dict)
        klass = get_writer_class(self.writer)
        writer = klass(root_path, images_path, data_filename)
        s = root_path + images_path + data_filename
        writer.update_template(
            {f: "{" + f + "}" for f in self._template_named_fields(s)}
        )
        return writer

    @property
    def file_extension(self):
        """As determined by the writer"""
        return get_writer_class(self.writer).get_file_extension()

    def get_writer_object(self):
        """This instantiates the writer class
        :returns bliss.scanning.writer.File:
        """
        return self.writer_object

    def get_writer_options(self):
        return self.writer_object.get_writer_options()

    def create_path(self, path: str) -> bool:
        """The path is created by the writer if the path if part
        of the data root, else by Bliss (subdir or outside data root).
        """
        return self.writer_object.create_path(path)

    def create_root_path(self):
        """Create the scan data directory"""
        self.create_path(self.root_path)

    def get_parent_node(self, create=True):
        """This method returns the parent node which should be used to publish new data

        :param bool create:
        :returns DatasetNode or None: can only return `None` when `create=False`
        """
        return self._get_node(self._db_path_items, create=create)

    def _get_node(self, db_path_items, create=True):
        """This method returns the parent node which should be used to publish new data

        :param list((str,str)) db_path_items:
        :param bool create:
        :returns DatasetNode or None: can only return `None` when `create=False`
        """
        groups = [
            (name, node_type)
            for name, node_type in db_path_items
            if node_type in ["proposal", "dataset_collection", "dataset"]
        ]

        data_policy_tree = RedisJsonTree(f"data_policy:{current_session.name}")

        node_path = ""
        for item_name, node_type in groups:
            node_path += "/" + item_name
            try:
                lock.acquire()
                node = data_policy_tree.get_node(node_path)
            except KeyError:
                if create:
                    node = data_policy_tree.create_node(node_path)
                    self._fill_node_info(node, node_type)
                else:
                    return None  # should raise instead...
            finally:
                lock.release()

        return node

    def _fill_node_info(self, node, node_type):
        """Add missing keys to node info"""
        pass

    def newproposal(self, proposal_name):
        raise NotImplementedError("No data policy enabled")

    def newcollection(self, collection_name, **kw):
        raise NotImplementedError("No data policy enabled")

    def newsample(self, collection_name, **kw):
        raise NotImplementedError("No data policy enabled")

    def newdataset(self, dataset_name, **kw):
        raise NotImplementedError("No data policy enabled")

    def clone(self):
        new_scan_saving = self.__class__(self.name)
        for s in self.SLOTS:
            setattr(new_scan_saving, s, getattr(self, s))
        return new_scan_saving

    @property
    def elogbook(self):
        return None

    def on_scan_run(self, save):
        """Called at the start of a scan (in Scan.run)"""
        if is_bliss_shell() and Path(gettempdir()) in Path(self.root_path).parents:
            logger.warning(
                f"scan data are currently saved under {gettempdir()}, where files are volatile."
            )


class ESRFScanSaving(BasicScanSaving):
    """Parameterized representation of the scan data file path
    according to the ESRF data policy

        <base_path>/<template>/<data_filename><file_extension>

    where

     - <base_path> depends on the proposal type
     - <template> is a fixed template
     - <data_filename> is a fixed template
     - <file_extension> depends on the select writer
    """

    # Not in Redis (instance attribute)
    SLOTS = BasicScanSaving.SLOTS + [
        "_icat_client",
        "_proposal_object",
        "_collection_object",
        "_dataset_object",
    ]

    # In Redis
    DEFAULT_VALUES = {
        # default and not removable values
        "images_path_template": "scan{scan_number}",
        "images_prefix": "{img_acq_device}_",
        "date_format": "%Y%m%d",
        "scan_number_format": "%04d",
        "dataset_number_format": "%04d",
        # saved properties in Redis:
        "_writer_module": "nexus",
        "_proposal": "",
        "_ESRFScanSaving__proposal_timestamp": 0,
        "_proposal_session_name": "",
        "_collection": "",
        "_dataset": "",
        "_mount": "",
        "_reserved_dataset": "",
    }

    # Not in Redis (class property)
    # Order important for resolving dependencies
    PROPERTY_ATTRIBUTES = BasicScanSaving.PROPERTY_ATTRIBUTES + [
        "template",
        "beamline",
        "proposal_name",
        "proposal_dirname",
        "proposal_session_name",
        "base_path",
        "collection_name",
        "dataset_name",
        "data_filename",
        "images_path_relative",
        "mount_point",
        "proposal",
        "collection",
        "dataset",
    ]

    # Not in Redis (class property not used in string templates)
    # Must be a subset of self._property_attributes
    NO_EVAL_PROPERTIES = BasicScanSaving.NO_EVAL_PROPERTIES | {
        "proposal",
        "collection",
        "dataset",
    }

    REDIS_SETTING_PREFIX = "esrf_scan_saving"

    def __init__(self, name, session_name=None):
        super().__init__(name, session_name)
        self._icat_client = None
        self._proposal_object = None
        self._collection_object = None
        self._dataset_object = None
        self._remove_deprecated_defaults()

    def _remove_deprecated_defaults(self):
        """Remove deprecated default parameters from Redis"""
        redis_keys = set(self._proxy.keys())

        if "_sample" in redis_keys:
            # Renamed default parameter from "_sample" to "_collection"
            # (bliss > 1.7.0)
            value = self._proxy["_sample"]
            self.remove("._sample")
            self._collection = value

        if "technique" in redis_keys:
            # Removed default parameter "technique"
            # (bliss > 1.8.0)
            self.remove(".technique")

    def __dir__(self):
        keys = super().__dir__()
        keys.extend(
            [
                "proposal_type",
                "icat_root_path",
                "icat_data_path",
                "icat_data_fullpath",
                "icat_register_datasets",
                "icat_register_dataset",
                "icat_info",
                "icat_investigation_info",
                "icat_dataset_info",
            ]
        )
        return keys

    @property
    def _session_config(self):
        """Session config or an empty dictionary, if there is no associated session"""
        session_name = self._session_name
        if session_name is None:
            return {}
        config = get_config()
        session_config = config.get_config(session_name)
        return session_config

    @property
    def _config_root(self):
        """Static config root"""
        return get_config().root

    @property
    def scan_saving_config(self):
        return self._session_config.get(
            "scan_saving", self._config_root.get("scan_saving", {})
        )

    @property
    def data_policy(self):
        return "ESRF"

    @property
    def icat_client(self):
        if self._icat_client is None:
            config = self.icat_client_config
            self._icat_client = icat_client_from_config(config)
        return self._icat_client

    @property
    def icat_client_config(self):
        if self.proposal_type == "tmp":
            return {"disable": True}
        else:
            return icat_client_config(
                bliss_session=self.session,
                proposal=self.proposal_name,
                beamline=self.beamline,
            )

    @property
    def images_path_relative(self):
        # Always relative due to the data policy
        return True

        # todo remove images_path_relative completely from here!

    @property
    def beamline(self):
        bl = self.scan_saving_config.get("beamline")
        if not bl:
            return "{beamline}"
        # Should contain only: alphanumeric, space-like, dash and underscore
        if not re.match(r"^[0-9a-zA-Z_\s\-]+$", bl):
            raise ValueError("Beamline name is invalid")
        # Normalize: lowercase alphanumeric
        return re.sub(r"[^-0-9a-z]", "", bl.lower())

    @autocomplete_property
    def proposal(self):
        """Nothing is created in Redis for the moment."""
        if self._proposal_object is None:
            # This is just for caching purposes
            self._ensure_proposal()
            self._proposal_object = self._get_proposal_object(create=True)
        return self._proposal_object

    @autocomplete_property
    def collection(self):
        """Nothing is created in Redis for the moment."""
        if self._collection_object is None:
            # This is just for caching purposes
            self._ensure_collection()
            self._collection_object = self._get_collection_object(create=True)
        return self._collection_object

    @autocomplete_property
    def sample(self):
        return self.collection

    @property_with_eval_dict
    def sample_name(self, eval_dict=None):
        # Property of ESRFScanSaving so that it can be used in a template
        return self.get_cached_property("dataset", eval_dict).sample_name

    @property_with_eval_dict
    def dataset(self, eval_dict=None):
        """The dataset will be created in Redis when it does not exist yet."""
        if self._dataset_object is None:
            # This is just for caching purposes
            self._ensure_dataset()
            self._dataset_object = self._get_dataset_object(
                create=True, eval_dict=eval_dict
            )
        return self._dataset_object

    @property
    def template(self):
        version = self.scan_saving_config.get("directory_structure_version", 3)
        if version == 1:
            return "{proposal_dirname}/{beamline}/{proposal_session_name}/{collection_name}/{collection_name}_{dataset_name}"
        elif version == 2:
            return "{proposal_dirname}/{beamline}/{proposal_session_name}/raw/{collection_name}/{collection_name}_{dataset_name}"
        elif version == 3:
            return "{proposal_dirname}/{beamline}/{proposal_session_name}/RAW_DATA/{collection_name}/{collection_name}_{dataset_name}"
        else:
            raise RuntimeError(
                "The scan saving key 'directory_structure_version' from the beamline configuration must be either 1, 2 or 3."
            )

    @with_eval_dict
    def _valid_proposal_session_names(self, eval_dict=None):
        base_path = self.get_cached_property("base_path", eval_dict)
        template = os.path.join(base_path, "{proposal_name}", "{beamline}")
        search_path = self.eval_template(template, eval_dict=eval_dict)
        if os.path.isdir(search_path):
            pattern = self._proposal_session_name_regex_pattern
            return [
                f.name
                for f in os.scandir(search_path)
                if f.is_dir() and bool(pattern.match(f.name))
            ]
        else:
            return []

    def _validate_name(self, value: Union[str, int, None]):
        if not isinstance(value, str):
            return
        _check_valid_in_path(value)

    @property
    def _icat_proposal_path(self):
        # See template
        return os.sep.join(self.icat_root_path.split(os.sep)[:-3])

    @property
    def _icat_collection_path(self):
        # See template
        return os.sep.join(self.icat_root_path.split(os.sep)[:-1])

    @property
    def _icat_dataset_path(self):
        # See template
        return self.icat_root_path

    @property_with_eval_dict
    def _db_path_keys(self, eval_dict=None):
        session = self.session
        base_path = self.get_cached_property("base_path", eval_dict).split(os.sep)
        base_path = [p for p in base_path if p]
        proposal = self.get_cached_property("proposal_name", eval_dict)
        collection = self.get_cached_property("collection_name", eval_dict)
        dataset = self.get_cached_property("dataset_name", eval_dict)
        # When dataset="0001" the DataNode.name will be the integer 1
        # so use the file name instead.
        # dataset = self.get_cached_property("dataset", eval_dict)
        return [session] + base_path + [proposal, collection, dataset]

    @property_with_eval_dict
    def _db_path_items(self, eval_dict=None):
        """For scan's parent node creation (see `get_parent_node`)

        :returns list(tuple):
        """
        parts = self.get_cached_property("_db_path_keys", eval_dict)
        types = ["container"] * len(parts)
        # See template:
        types[-3] = "proposal"
        types[-2] = "dataset_collection"
        types[-1] = "dataset"
        return list(zip(parts, types))

    @property_with_eval_dict
    def _db_proposal_items(self, eval_dict=None):
        return self.get_cached_property("_db_path_items", eval_dict)[:-2]

    @property_with_eval_dict
    def _db_collection_items(self, eval_dict=None):
        return self.get_cached_property("_db_path_items", eval_dict)[:-1]

    @property_with_eval_dict
    def _db_dataset_items(self, eval_dict=None):
        return self.get_cached_property("_db_path_items", eval_dict)

    def _fill_node_info(self, node, node_type):
        """Add missing keys to node info"""
        if node_type == "proposal":
            info = {
                "__name__": self.proposal_name,
                "__path__": self._icat_proposal_path,
                "__metadata__": {},
                "__frozen__": False,
            }
        elif node_type == "dataset_collection":
            info = {
                "__name__": self.collection_name,
                "__path__": self._icat_collection_path,
                "__metadata__": {"Sample_name": self.collection_name},
                "__frozen__": False,
            }
        elif node_type == "dataset":
            info = {
                "__name__": self.dataset_name,
                "__path__": self._icat_dataset_path,
                "__metadata__": {
                    "startDate": datetime.datetime.now().astimezone().isoformat()
                },
                "__frozen__": False,
                "__closed__": False,
                "__registered__": False,
            }
        else:
            return

        node_info = node.get()
        update = False
        for k, v in info.items():
            if k not in node_info:
                node_info[k] = v
                update = True
        if update:
            node.set(node_info)

    @with_eval_dict
    def _get_proposal_node(self, create=True, eval_dict=None):
        """This method returns the proposal node

        :param bool create:
        :returns ProposalNode or None: can only return `None` when `create=False`
        """
        db_path_items = self.get_cached_property("_db_proposal_items", eval_dict)
        return self._get_node(db_path_items, create=create)

    @with_eval_dict
    def _get_collection_node(self, create=True, eval_dict=None):
        """This method returns the collection node

        :param bool create:
        :returns DatasetCollectionNode or None: can only return `None` when `create=False`
        """
        db_path_items = self.get_cached_property("_db_collection_items", eval_dict)
        return self._get_node(db_path_items, create=create)

    @with_eval_dict
    def _get_dataset_node(self, create=True, eval_dict=None):
        """This method returns the dataset node

        :param bool create:
        :returns DatasetNode or None: can only return `None` when `create=False`
        """
        db_path_items = self.get_cached_property("_db_dataset_items", eval_dict)
        return self._get_node(db_path_items, create=create)

    @property_with_eval_dict
    def base_path(self, eval_dict=None):
        """Root directory depending in the proposal type (inhouse, visitor, tmp)"""
        return self._get_base_path(icat=False, eval_dict=eval_dict)

    @property_with_eval_dict
    def icat_base_path(self, eval_dict=None):
        """ICAT root directory depending in the proposal type (inhouse, visitor, tmp)"""
        return self._get_base_path(icat=True, eval_dict=eval_dict)

    @property
    def date(self):
        if self._ESRFScanSaving__proposal_timestamp:
            tm = datetime.datetime.fromtimestamp(
                self._ESRFScanSaving__proposal_timestamp
            )
        else:
            tm = datetime.datetime.now()
        return tm.strftime(self.date_format)

    def _freeze_date(self):
        self._ESRFScanSaving__proposal_timestamp = time.time()

    def _unfreeze_date(self):
        self._ESRFScanSaving__proposal_timestamp = 0

    @with_eval_dict
    def _get_base_path(self, icat=False, eval_dict=None):
        """Root directory depending in the proposal type (inhouse, visitor, tmp)"""
        ptype = self.get_cached_property("proposal_type", eval_dict)
        # When <type>_data_root is missing: use hardcoded default
        # When icat_<type>_data_root is missing: use <type>_data_root
        if ptype == "inhouse":
            template = self._get_mount_point(
                "inhouse_data_root", "/data/{beamline}/inhouse"
            )
            if icat:
                template = self._get_mount_point("icat_inhouse_data_root", template)
        elif ptype == "visitor":
            template = self._get_mount_point("visitor_data_root", "/data/visitor")
            if icat:
                template = self._get_mount_point("icat_visitor_data_root", template)
        else:
            template = self._get_mount_point("tmp_data_root", "/data/{beamline}/tmp")
            if icat:
                template = self._get_mount_point("icat_tmp_data_root", template)
        return self.eval_template(template, eval_dict=eval_dict)

    def _get_mount_point(self, key, default):
        """Get proposal type's mount point which defines `base_path`

        :param str key: scan saving configuration dict key
        :param str default: when key is not in configuration
        :returns str:
        """
        mount_points = self._mount_points_from_config(key, default)
        current_mp = mount_points.get(self.mount_point, None)
        if current_mp is None:
            # Take the first mount point when the current one
            # is not defined for this proposal type
            return mount_points[next(iter(mount_points.keys()))]
        else:
            return current_mp

    def _mount_points_from_config(self, key, default):
        """Get all mount points for the proposal type.

        :param str key: scan saving configuration dict key
        :param str default: when key is not in configuration
                            it returns {"": default})
        :returns dict: always at least one key-value pair
        """
        mount_points = self.scan_saving_config.get(key, default)
        if isinstance(mount_points, str):
            return {"": mount_points}
        else:
            return mount_points.to_dict()

    @property
    def mount_points(self):
        """All mount points of all proposal types

        :returns set(str):
        """
        mount_points = set()
        for k in ["inhouse_data_root", "visitor_data_root", "tmp_data_root"]:
            mount_points |= self._mount_points_from_config(k, "").keys()
            mount_points |= self._mount_points_from_config(f"icat_{k}", "").keys()
        return mount_points

    @property
    def mount_point(self):
        """Current mount point (defines `base_path` selection
        from scan saving configuration) for all proposal types
        """
        if self._mount is None:
            self._mount = ""
        return self._mount

    @mount_point.setter
    def mount_point(self, value):
        """
        :param str value:
        :raises ValueError: not in the available mount points
        """
        choices = self.mount_points
        if value not in choices:
            raise ValueError(f"The only valid mount points are {choices}")
        self._mount = value

    @property_with_eval_dict
    def icat_root_path(self, eval_dict=None):
        """Directory of the scan *data file* reachable by ICAT"""
        base_path = self.get_cached_property("icat_base_path", eval_dict)
        return self._get_root_path(base_path, eval_dict=eval_dict)

    @property_with_eval_dict
    def icat_data_path(self, eval_dict=None):
        """Full path for the scan *data file* without the extension,
        reachable by ICAT
        """
        root_path = self.get_cached_property("icat_root_path", eval_dict)
        return self._get_data_path(root_path, eval_dict=eval_dict)

    @property_with_eval_dict
    def icat_data_fullpath(self, eval_dict=None):
        """Full path for the scan *data file* with the extension,
        reachable by ICAT
        """
        data_path = self.get_cached_property("icat_data_path", eval_dict)
        return self._get_data_fullpath(data_path, eval_dict=eval_dict)

    @property
    def data_filename(self):
        """File name template without extension"""
        return "{collection_name}_{dataset_name}"

    def _ensure_proposal(self):
        """Make sure a proposal is selected"""
        if not self._proposal:
            self.proposal_name = None
            self.proposal_session_name = None

    def _ensure_collection(self):
        """Make sure a collection is selected"""
        if not self._collection:
            self.collection_name = None

    def _ensure_dataset(self):
        """Make sure a dataset is selected"""
        if not self._dataset:
            self.dataset_name = None

    @property_with_eval_dict
    def proposal_name(self, eval_dict=None):
        if not self._proposal:
            self.set_cached_property("proposal_name", None, eval_dict)
        return self.eval_template(self._proposal, eval_dict=eval_dict)

    @proposal_name.setter
    def proposal_name(self, name, eval_dict=None):
        self._set_proposal_name(name, eval_dict=eval_dict)

    def _set_proposal_name(self, name, eval_dict=None, reset=False):
        if name:
            # Should contain only: alphanumeric, space-like, dash and underscore
            if not re.match(r"^[0-9a-zA-Z_\s\-]+$", name):
                raise ValueError("Proposal name is invalid")
            # Normalize: lowercase alphanumeric
            name = re.sub(r"[^0-9a-z]", "", name.lower())
        else:
            yymm = time.strftime("%y%m")
            name = f"{{beamline}}{yymm}"
        if not reset and name == self._proposal:
            return
        self._close_dataset(eval_dict=eval_dict)
        self._close_collection()
        self._close_proposal(eval_dict=eval_dict)
        self._proposal = name
        self._proposal_session_name = ""
        self._collection = ""
        self._dataset = ""
        self._freeze_date()
        self.icat_client.start_investigation(
            beamline=self.beamline, proposal=self.proposal_name
        )
        # TODO: The ICAT client used by Flint is not getting
        # the proposal name from Redis but gets it at startup.
        # So we have to restart Flint at this point.
        restart_flint(creation_allowed=False)

    @property_with_eval_dict
    def proposal_dirname(self, eval_dict=None):
        dirname = self.get_cached_property("proposal_name", eval_dict=eval_dict)
        if not dirname.isdigit():
            return dirname
        proposal_type = self.get_cached_property("proposal_type", eval_dict=eval_dict)
        if proposal_type != "visitor":
            return dirname
        # TID does not allow directories with only digits. Add the beamline
        # letters as prefix (e.g. "BM") and remove leading zeros after the
        # beamline name. For example proposal 02-01234 is saved in /data/visitor/bm021234
        beamline = self.get_cached_property("beamline", eval_dict=eval_dict)
        tmp = re.sub("[0-9]", "", beamline) + dirname
        if not tmp.startswith(beamline):
            return dirname
        dirname = beamline + str(int(tmp[len(beamline) :]))
        return dirname

    @property_with_eval_dict
    def proposal_session_name(self, eval_dict=None):
        if not self._proposal_session_name:
            self.set_cached_property("proposal_session_name", None, eval_dict)
        return self.eval_template(self._proposal_session_name, eval_dict=eval_dict)

    @proposal_session_name.setter
    def proposal_session_name(self, name, eval_dict=None):
        if name and name == self._proposal_session_name:
            return
        proposal_session_names = self._valid_proposal_session_names(eval_dict=eval_dict)
        if name not in proposal_session_names:
            name = self._select_proposal_session_name(proposal_session_names)
        self._proposal_session_name = name
        self._collection = ""
        self._dataset = ""

    @property
    def _proposal_session_name_format(self):
        return "%Y%m%d"

    @property
    def _proposal_session_name_regex_pattern(self):
        d = r"([0-2]\d|3[01])"
        m = r"(0\d|1[0-2])"
        Y = r"(\d{4})"
        return re.compile(f"^{Y}{m}{d}$")

    def _select_proposal_session_name(self, proposal_session_names):
        if len(proposal_session_names) == 1:
            # There is only one valid session
            return proposal_session_names[0]
        elif proposal_session_names:
            # Select the current session based on the date
            now = datetime.date.today()
            dates = [
                datetime.datetime.strptime(s, self._proposal_session_name_format).date()
                for s in proposal_session_names
            ]
            dates = sorted(dates)
            for idx, dt in enumerate(dates):
                if int((dt - now).total_seconds()) > 0:
                    selected = dates[max(0, idx - 1)]
                    break
            else:
                selected = dates[-1]
            return selected.strftime(self._proposal_session_name_format)
        else:
            # Select the default session (first of this month)
            dt = datetime.date.today().replace(day=1)
            return dt.strftime(self._proposal_session_name_format)

    @property_with_eval_dict
    def proposal_type(self, eval_dict=None):
        proposal_name = self.get_cached_property("proposal_name", eval_dict)
        beamline = self.get_cached_property("beamline", eval_dict)
        return self._proposal_type_from_name(proposal_name, beamline)

    def _proposal_type_from_name(self, proposal_name: str, beamline: str) -> str:
        if proposal_name.startswith(beamline):
            return "inhouse"
        inhouse_prefixes = self.scan_saving_config.get(
            "inhouse_proposal_prefixes", tuple()
        )
        for proposal_prefix in inhouse_prefixes:
            proposal_prefix = re.sub(r"[^0-9a-z]", "", proposal_prefix.lower())
            if proposal_name.startswith(proposal_prefix):
                return "inhouse"
        default_tmp_prefixes = "tmp", "temp", "test"
        tmp_prefixes = self.scan_saving_config.get(
            "tmp_proposal_prefixes", default_tmp_prefixes
        )
        for proposal_prefix in tmp_prefixes:
            proposal_prefix = re.sub(r"[^0-9a-z]", "", proposal_prefix.lower())
            if proposal_name.startswith(proposal_prefix):
                return "tmp"
        return "visitor"

    @property_with_eval_dict
    def collection_name(self, eval_dict=None):
        if not self._collection:
            self.set_cached_property("collection_name", None, eval_dict)
        return self._collection

    @collection_name.setter
    def collection_name(self, name: Union[str, None], eval_dict=None):
        self._set_collection_name(name, eval_dict=eval_dict)

    @with_eval_dict
    def _set_collection_name(self, name: Union[str, None], eval_dict=None):
        if name:
            self._validate_name(name)
        else:
            name = "sample"
        self._close_dataset(eval_dict=eval_dict)
        self._close_collection()
        self._ensure_proposal()
        self._collection = name
        self._dataset = ""

    @property_with_eval_dict
    def dataset_name(self, eval_dict=None):
        if not self._dataset:
            self.set_cached_property("dataset_name", None, eval_dict)
        return self._dataset

    @dataset_name.setter
    def dataset_name(self, value: Union[str, int, None], eval_dict=None):
        self._validate_name(value)
        self._close_dataset(eval_dict=eval_dict)
        self._ensure_proposal()
        self._ensure_collection()
        reserved = self._reserved_datasets()
        original_dataset_name = self._dataset
        original_reserved_dataset = self._reserved_dataset
        try:
            self._dataset = "{dataset_name}"
            root_path_template = self.root_path
            for dataset_name in self._dataset_name_generator(value):
                root_path = root_path_template.format(dataset_name=dataset_name)
                if not os.path.exists(root_path) and root_path not in reserved:
                    self._reserved_dataset = root_path
                    reserved = self._reserved_datasets()
                    if root_path in reserved:
                        continue  # another session reserved it in the mean time
                    self._dataset = dataset_name
                    break
        except BaseException:
            self._reserved_dataset = original_reserved_dataset
            self._dataset = original_dataset_name
            raise

    def _reserved_datasets(self):
        """The dataset directories reserved by all sessions,
        whether the directories exist or not.
        """
        reserved = set()
        pattern = f"parameters:{self.REDIS_SETTING_PREFIX}:*:default"
        self_name = self.name
        for key in scan_redis(match=pattern):  # new connection to avoid cache
            name = key.split(":")[2]
            if name == self_name:
                continue
            scan_saving = self.__class__(name)
            reserved.add(scan_saving._reserved_dataset)
        return reserved

    def _dataset_name_generator(self, prefix):
        """Generates dataset names

        When prefix is a number (provided as int or str):
        "0005", "0006", ...

        Without prefix:
        "0001", "0002", ...

        All other cases:
        "prefix", "prefix_0002", "prefix_0003", ...

        :param int or str prefix:
        :yields str:
        """
        # Prefix and start index
        start = 0
        if prefix:
            if isinstance(prefix, str):
                if prefix.isdigit():
                    start = int(prefix)
                    prefix = ""
            else:
                start = int(prefix)
                prefix = ""
        else:
            prefix = ""
        # Yield the prefix as first name
        if prefix:
            start = max(start, 2)
            yield prefix
        else:
            start = max(start, 1)
        # Yield consecutive names
        if prefix:
            template = f"{prefix}_{self.dataset_number_format}"
        else:
            template = f"{self.dataset_number_format}"
        for i in itertools.count(start):
            yield template % i
            gevent.sleep()

    @with_eval_dict
    def _on_data_policy_changed(self, msg, elogbook=True, eval_dict=None):
        self._emit_data_policy_event(msg, eval_dict=eval_dict)
        root_path = self.get_cached_property("root_path", eval_dict)

        msg += f"\nData path: {root_path}"
        if elogbook:
            logtools.elog_info(msg)

        confirmed, unconfirmed = self.icat_confirm_datasets(eval_dict=eval_dict)
        n = len(unconfirmed)
        if n > 1:
            msg += f"\nNumber of unconfirmed ICAT dataset registrations: {n}"
            if confirmed is None:
                msg += f" ({self.icat_client.reason_for_missing_information})"
        print(msg)

    def newproposal(self, proposal_name, session_name=None, prompt=False):
        """The proposal will be created in Redis if it does not exist already."""
        # beware: self.proposal getter and setter do different actions
        self.proposal_name = proposal_name
        if not session_name and prompt and is_bliss_shell():
            from bliss.shell.cli.user_dialog import UserChoice
            from bliss.shell.cli import pt_widgets

            values = self._valid_proposal_session_names()
            if len(values) > 1:
                values = list(zip(values, values))
                dlg = UserChoice(
                    label="Session of proposal " + self.proposal_name, values=values
                )
                session_name = pt_widgets.display(dlg)
        self.proposal_session_name = session_name
        self._on_data_policy_changed(
            f"Proposal set to '{self.proposal_name}' (session '{self.proposal_session_name}')"
        )

    def newcollection(self, collection_name, sample_name=None, sample_description=None):
        """The dataset collection will be created in Redis if it does not exist already."""
        # beware: self.collection getter and setter do different actions
        self.collection_name = collection_name
        self._on_data_policy_changed(
            f"Dataset collection set to '{self.collection_name}'"
        )

        # fill metadata if provided
        if sample_name:
            self.collection.sample_name = sample_name
        if sample_description is not None:
            self.collection.sample_description = sample_description

    def newsample(self, collection_name, description=None):
        """Same as `newcollection` with sample name equal to the collection name."""
        self.newcollection(
            collection_name, sample_name=collection_name, sample_description=description
        )

    def newdataset(
        self, dataset_name, description=None, sample_name=None, sample_description=None
    ):
        """The dataset will be created in Redis if it does not exist already.
        Metadata will be gathered if not already done. RuntimeError is raised
        when the dataset is already closed.

        If `newdataset` is not used, the metadata gathering is done at the
        start of the first scan that aves data.
        """
        # beware: self.dataset_name getter and setter do different actions
        _dataset = self._dataset
        self.dataset_name = dataset_name
        try:
            self._init_dataset()
        except Exception:
            if _dataset is not None:
                self._dataset = _dataset
            raise

        self._on_data_policy_changed(f"Dataset set to '{self.dataset_name}'")

        if sample_name:
            self.dataset.sample_name = sample_name
        if sample_description is not None:
            self.dataset.sample_description = sample_description
        if description is not None:
            self.dataset.description = description

    def icat_register_dataset(
        self, dataset_name_or_id: Union[DatasetId, str], raise_on_error: bool = True
    ):
        try:
            dset = self._get_dataset(dataset_name_or_id)
            dset.register_with_icat(self.icat_client, raise_on_error=raise_on_error)
        except Exception as e:
            if raise_on_error:
                raise
            logtools.log_exception(self.proposal, str(e))
        else:
            print(f"Dataset '{dataset_name_or_id}' has been send to ICAT")

    def icat_save_dataset(
        self, dataset_name_or_id: Union[DatasetId, str], raise_on_error: bool = True
    ):
        try:
            dset = self._get_dataset(dataset_name_or_id)

            basename = os.path.splitext(os.path.basename(dset.path))[0] + ".xml"
            dirname = os.path.join(self.icat_directory, basename)

            dset.save_for_icat(self.icat_client, dirname)
        except Exception as e:
            if raise_on_error:
                raise
            logtools.elog_error(str(e))
            logtools.log_exception(self.proposal, str(e))
        else:
            print(f"Dataset '{dataset_name_or_id}' has been saved")

    @property
    def icat_directory(self) -> str:
        dirname = os.path.dirname(os.path.dirname(os.path.dirname(self.filename)))
        return os.path.join(dirname, "__icat__")

    def _get_dataset(self, dataset_name_or_id: Union[DatasetId, str]) -> Dataset:
        proposal = self.proposal
        dataset = proposal.get_dataset(dataset_name_or_id)
        if dataset is None:
            raise RuntimeError(
                f"dataset '{dataset_name_or_id}' does not exist in Redis"
            )
        if is_null_client(self.icat_client):
            raise RuntimeError(
                f"Dataset '{dataset_name_or_id}' cannot be send to ICAT ({self.icat_client.reason_for_missing_information})"
            )
        return dataset

    def icat_register_datasets(
        self, raise_on_error=True, timeout: Optional[bool] = None
    ):
        _, unconfirmed = self.icat_confirm_datasets(timeout=timeout)
        if not unconfirmed:
            print("All datasets are already registered in ICAT")
        for dataset_id in unconfirmed:
            self.icat_register_dataset(dataset_id, raise_on_error=raise_on_error)
        print("")
        self.icat_info(timeout=timeout)

    def icat_investigation_info(self, timeout: Optional[float] = None):
        print(
            self.icat_client.investigation_info_string(
                beamline=self.beamline, proposal=self.proposal_name, timeout=timeout
            )
        )

    def icat_dataset_info(self, timeout: Optional[bool] = None):
        confirmed, unconfirmed = self.icat_confirm_datasets(timeout=timeout)
        if confirmed is None:
            print(f"Datasets: {len(unconfirmed)} unconfirmed, ??? confirmed")
        else:
            print(
                f"Datasets: {len(unconfirmed)} unconfirmed, {len(confirmed)} confirmed"
            )
        print("")
        dataset_info = self.proposal.unconfirmed_dataset_info_string()
        if dataset_info:
            print(dataset_info)

    def icat_info(self, timeout: Optional[float] = None):
        self.icat_investigation_info(timeout=timeout)
        print("")
        self.icat_dataset_info(timeout=timeout)

    @with_eval_dict
    def icat_confirm_datasets(
        self, eval_dict=None, timeout: Optional[float] = None
    ) -> tuple[list, list]:
        """Compare the list of unconfirmed datasets in Redis with
        the list of confirmed dataset in ICAT and confirm datasets.
        """
        proposal = self.proposal
        proposal_name = self.get_cached_property("proposal_name", eval_dict)
        beamline = self.get_cached_property("beamline", eval_dict)
        confirmed = self.icat_client.registered_dataset_ids(
            beamline=beamline, proposal=proposal_name, timeout=timeout
        )
        unconfirmed = proposal.unconfirmed_dataset_ids
        if confirmed is not None:
            for dataset_id in set(unconfirmed) & set(confirmed):
                dataset = proposal.get_dataset(dataset_id)
                if dataset is None:
                    continue
                dataset.confirm_registration()
        return confirmed, proposal.unconfirmed_dataset_ids

    def endproposal(self):
        """Close the active dataset (if any) and go to the default inhouse proposal"""
        self._set_proposal_name(None, reset=True)
        self._on_data_policy_changed(
            f"Proposal set to '{self.proposal_name}' (session '{self.proposal_session_name}')",
            elogbook=False,
        )

    def enddataset(self):
        """Close the active dataset (if any) and go the the next dataset"""
        self.dataset_name = None
        self._on_data_policy_changed(
            f"Dataset set to '{self.dataset_name}'", elogbook=False
        )

    @with_eval_dict
    def _emit_data_policy_event(self, event, eval_dict):
        data_path = self.get_cached_property("root_path", eval_dict)
        if self._session_name is None:
            session = current_session
        else:
            session = get_config().get(self._session_name)
        session._emit_event(
            ESRFDataPolicyEvent.Change, message=event, data_path=data_path
        )

    def _get_proposal_object(self, create=True):
        """Create a new Proposal instance.

        :param bool create: Create in Redis when it does not exist
        """
        if not self._proposal:
            raise RuntimeError("proposal not specified")
        node = self._get_proposal_node(create=create)
        if node is None:
            raise RuntimeError("proposal does not exist in Redis")
        return Proposal(node)

    def _get_collection_object(self, create=True):
        """Create a new DatasetCollection instance.

        :param bool create: Create in Redis when it does not exist
        """
        if not self._proposal:
            raise RuntimeError("proposal not specified")
        if not self._collection:
            raise RuntimeError("collection not specified")
        node = self._get_collection_node(create=create)
        if node is None:
            raise RuntimeError("collection does not exist in Redis")
        return DatasetCollection(node)

    @with_eval_dict
    def _get_dataset_object(self, create=True, eval_dict=None):
        """Create a new Dataset instance. The Dataset may be already closed,
        this is not checked in this method.

        :param bool create: Create in Redis when it does not exist
        :raises RuntimeError: this happens when
                            - the dataset is not fully defined yet
                            - the dataset does not exist in Redis and create=False
        """
        if not self._proposal:
            raise RuntimeError("proposal not specified")
        if not self._collection:
            raise RuntimeError("collection not specified")
        if not self._dataset:
            raise RuntimeError("dataset not specified")
        node = self._get_dataset_node(create=create, eval_dict=eval_dict)
        if node is None:
            raise RuntimeError("dataset does not exist in Redis")
        return Dataset(node)

    @property
    def elogbook(self):
        return self.icat_client

    @with_eval_dict
    def _close_proposal(self, eval_dict=None):
        """Close the current proposal."""
        if self._proposal:
            self._save_unconfirmed_datasets(eval_dict=eval_dict, raise_on_error=False)

            # clear proposal from the json policy tree in Redis
            node = self._proposal_object._node
            tree = node._tree
            tree.delete_node(node._path)

        self._proposal_object = None
        self._proposal = ""
        self._icat_client = None

    def _save_unconfirmed_datasets(
        self, eval_dict=None, raise_on_error: bool = True, timeout=10
    ) -> bool:
        print(
            f"Check whether all datasets are registered with ICAT ... (timeout = {timeout} s)"
        )
        t0 = time.time()
        unconfirmed = set()
        while (time.time() - t0) < timeout:
            _, unconfirmed = self.icat_confirm_datasets(
                eval_dict=eval_dict, timeout=timeout
            )
            if not unconfirmed:
                break
            gevent.sleep(0.5)

        if not unconfirmed:
            return
        msg = f'Unconfirmed datasets are stored in {self.icat_directory}\nYou may need to send them to ICAT manually with the command\n\n  icat-store-from-file "{self.icat_directory}/*.xml"\n'
        logtools.log_warning(self.proposal, msg)
        logtools.elog_warning(msg)
        for dataset_id in unconfirmed:
            self.icat_save_dataset(dataset_id, raise_on_error=raise_on_error)

    def _close_collection(self):
        """Close the current collection."""
        self._collection_object = None
        self._collection = ""

    @with_eval_dict
    def _close_dataset(self, eval_dict=None):
        """Close the current dataset. This will NOT create the dataset in Redis
        if it does not exist yet. If the dataset if already closed it does NOT
        raise an exception.
        """
        dataset = self._dataset_object
        if dataset is None:
            # The dataset object has not been cached
            try:
                dataset = self._get_dataset_object(create=False, eval_dict=eval_dict)
            except RuntimeError:
                # The dataset is not fully defined or does not exist.
                # Do nothing in that case.
                dataset = None

        if dataset is not None:
            if not dataset.is_closed:
                try:
                    # Finalize in Redis and send to ICAT
                    dataset.close(self.icat_client)
                except Exception as e:
                    if (
                        not dataset.node.exists
                        or dataset.collection is None
                        or dataset.proposal is None
                        or not dataset.collection.node.exists
                        or not dataset.proposal.node.exists
                    ):
                        # Failure due to missing Redis nodes: recreate them and try again
                        self.get_parent_node(create=True)
                        dataset = self._get_dataset_object(
                            create=False, eval_dict=eval_dict
                        )
                        try:
                            dataset.close(self.icat_client, raise_on_error=False)
                        except Exception as e2:
                            self._dataset_object = None
                            self._dataset = ""
                            raise RuntimeError("The dataset cannot be closed.") from e2
                        else:
                            self._dataset_object = None
                            self._dataset = ""
                            logtools.elog_warning(
                                f"The ICAT metadata of {self._dataset} is incomplete."
                            )
                            raise RuntimeError(
                                "The dataset was closed but its ICAT metadata is incomplete."
                            ) from e

        self._dataset_object = None
        self._dataset = ""

    def on_scan_run(self, save):
        """Called at the start of a scan (in Scan.run)"""
        if save:
            self._init_dataset()

    def _init_dataset(self):
        """The dataset will be created in Redis if it does not exist already.
        Metadata will be gathered if not already done. RuntimeError is raised
        when the dataset is already closed.
        """
        dataset = self.dataset  # Created in Redis when missing
        if dataset.is_closed:
            raise RuntimeError("Dataset is already closed (choose a different name)")
        dataset.gather_metadata(on_exists="skip")

    @with_eval_dict
    def get_data_info(self, eval_dict=None):
        lst = super().get_data_info()
        proposal_name = self.get_cached_property("proposal_name", eval_dict)
        beamline = self.get_cached_property("beamline", eval_dict)
        investigation_summary = self.icat_client.investigation_summary(
            beamline=beamline, proposal=proposal_name
        )
        for name, value in investigation_summary:
            lst.append(["ICAT", name, value])
        confirmed, unconfirmed = self.icat_confirm_datasets(eval_dict=eval_dict)
        if confirmed is None:
            lst.append(
                ["ICAT", "datasets", f"{len(unconfirmed)} unconfirmed, ??? confirmed"]
            )
        else:
            lst.append(
                [
                    "ICAT",
                    "datasets",
                    f"{len(unconfirmed)} unconfirmed, {len(confirmed)} confirmed",
                ]
            )
        return lst


# Characters that cannot be used in file or directory names:
#  - os.sep is forbidding because it adds another directory level
#  - "{" and "}" are forbidden because the name is used in
#    “new style” string formatting (see `ESRFScanSaving.template`)
#  - "%" is forbidden because the name can be used in “old style”
#    string formatting (% Operator)
#  - the null byte "\x00" is forbidden because in C it marks the end
#    of a string
#  - paths need to be accesible from Windows
#    https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file
#  - paths might be used within an url. So it must not conflict with it synthax
_FORBIDDEN_CHARS_BASE = {os.sep, "{", "}", "%", "\x00"}
_FORBIDDEN_CHARS_WINDOWS = {"<", ">", ":", '"', "'", "/", "\\", "|", "?", "*"} | {
    chr(i) for i in range(32)
}
_FORBIDDEN_CHARS_URL = {"@", "#", ":", "?"}
_FORBIDDEN_CHARS = (
    _FORBIDDEN_CHARS_BASE | _FORBIDDEN_CHARS_WINDOWS | _FORBIDDEN_CHARS_URL
)


def _check_valid_in_path(value: str) -> None:
    """Checks whether the string can be use in a file or directory name"""
    forbidden = set(value) & set(_FORBIDDEN_CHARS)
    if forbidden:
        forbidden = ", ".join([repr(c) for c in forbidden])
        raise ValueError(f"Forbidden characters were used: {forbidden}")
