# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.


# Imports

from __future__ import annotations

import platform
import os
import sys
import json
import errno
import codecs
import shutil
import logging
import argparse
import weakref
import socket
import signal
import traceback
import pkgutil
import tempfile
import gevent
import subprocess
import flask
import redis
import time
from functools import reduce

from ruamel.yaml import YAML, YAMLError
from contextlib import contextmanager, ExitStack
from gevent import select
import gevent.event
from gevent.pywsgi import WSGIServer
from gevent.socket import cancel_wait_ex

from bliss.common import event
from bliss.config.conductor import protocol
from bliss.config.conductor.web.app_dispatcher import create_app

from bliss.config import redis as redis_conf
from bliss.config.conductor import client as client_utils
from bliss.config.conductor import connection as connection_utils

from blissdata.redis_engine.store import DataStore

try:
    import win32api
except ImportError:
    IS_WINDOWS = False
else:
    IS_WINDOWS = True


# Globals

_waitstolen = dict()
_options = None
_lock_object = {}
_client_to_object = weakref.WeakKeyDictionary()
_client_to_name = weakref.WeakKeyDictionary()
_waiting_lock = weakref.WeakKeyDictionary()
uds_port_name = None

beacon_logger = logging.getLogger("beacon")
tango_logger = beacon_logger.getChild("tango")
redis_logger = beacon_logger.getChild("redis")
redis_data_logger = beacon_logger.getChild("redis_data")
memory_tracker_logger = beacon_logger.getChild("memtracker")
web_logger = beacon_logger.getChild("web")
log_server_logger = beacon_logger.getChild("log_server")
log_viewer_logger = beacon_logger.getChild("log_viewer")

_LOCAL_KEY_STORAGE: dict[str, str] = {}


class _WaitStolenReply(object):
    def __init__(self, stolen_lock):
        self._stolen_lock = dict()
        for client, objects in stolen_lock.items():
            self._stolen_lock[client] = b"|".join(objects)
        self._client2info = dict()

    def __enter__(self):
        for client, message in self._stolen_lock.items():
            event = gevent.event.Event()
            client2sync = _waitstolen.setdefault(message, dict())
            client2sync[client] = event
            client.sendall(protocol.message(protocol.LOCK_STOLEN, message))
        return self

    def __exit__(self, *args, **keys):
        for client, message in self._stolen_lock.items():
            client2sync = _waitstolen.pop(message, None)
            if client2sync is not None:
                client2sync.pop(client, None)
            if client2sync:
                _waitstolen[message] = client2sync

    def wait(self, timeout):
        with gevent.Timeout(
            timeout, RuntimeError("some client(s) didn't reply to stolen lock")
        ):
            for client, message in self._stolen_lock.items():
                client2sync = _waitstolen.get(message)
                if client2sync is not None:
                    sync = client2sync.get(client)
                    sync.wait()


# Methods


def _releaseAllLock(client_id):
    objset = _client_to_object.pop(client_id, set())
    for obj in objset:
        _lock_object.pop(obj)
    # Inform waiting client
    tmp_dict = dict(_waiting_lock)
    for client_sock, tlo in tmp_dict.items():
        try_lock_object = set(tlo)
        if try_lock_object.intersection(objset):
            _waiting_lock.pop(client_sock)
            try:
                client_sock.sendall(protocol.message(protocol.LOCK_RETRY))
            except OSError:
                # maybe this client is dead or whatever
                continue


def _lock(client_id, prio, lock_obj, raw_message):
    all_free = True
    for obj in lock_obj:
        socket_id, compteur, lock_prio = _lock_object.get(obj, (None, None, None))
        if socket_id and socket_id != client_id:
            if prio > lock_prio:
                continue
            all_free = False
            break

    if all_free:
        stolen_lock = {}
        for obj in lock_obj:
            socket_id, compteur, lock_prio = _lock_object.get(obj, (client_id, 0, prio))
            if socket_id != client_id:  # still lock
                pre_obj = stolen_lock.get(socket_id, None)
                if pre_obj is None:
                    stolen_lock[socket_id] = [obj]
                else:
                    pre_obj.append(obj)
                _lock_object[obj] = (client_id, 1, prio)
                objset = _client_to_object.get(socket_id, set())
                objset.remove(obj)
            else:
                compteur += 1
                new_prio = lock_prio > prio and lock_prio or prio
                _lock_object[obj] = (client_id, compteur, new_prio)

        try:
            with _WaitStolenReply(stolen_lock) as w:
                w.wait(3.0)
        except RuntimeError:
            beacon_logger.warning("some client(s) didn't reply to the stolen lock")

        obj_already_locked = _client_to_object.get(client_id, set())
        _client_to_object[client_id] = set(lock_obj).union(obj_already_locked)

        client_id.sendall(protocol.message(protocol.LOCK_OK_REPLY, raw_message))
    else:
        _waiting_lock[client_id] = lock_obj


def _unlock(client_id, priority, unlock_obj):
    unlock_object = []
    client_locked_obj = _client_to_object.get(client_id, None)
    if client_locked_obj is None:
        return

    for obj in unlock_obj:
        socket_id, compteur, prio = _lock_object.get(obj, (None, None, None))
        if socket_id and socket_id == client_id:
            compteur -= 1
            if compteur <= 0:
                _lock_object.pop(obj)
                try:
                    client_locked_obj.remove(obj)
                    _lock_object.pop(obj)
                except KeyError:
                    pass
                unlock_object.append(obj)
            else:
                _lock_object[obj] = (client_id, compteur, prio)

    unlock_object = set(unlock_object)
    tmp_dict = dict(_waiting_lock)
    for client_sock, tlo in tmp_dict.items():
        try_lock_object = set(tlo)
        if try_lock_object.intersection(unlock_object):
            _waiting_lock.pop(client_sock)
            client_sock.sendall(protocol.message(protocol.LOCK_RETRY))


def _clean(client):
    _releaseAllLock(client)


def _send_redis_info(client_id, local_connection):
    port = _options.redis_port
    host = socket.gethostname()
    if local_connection:
        port = _options.redis_socket
        host = "localhost"

    contents = b"%s:%s" % (host.encode(), str(port).encode())

    client_id.sendall(protocol.message(protocol.REDIS_QUERY_ANSWER, contents))


def _send_redis_data_server_info(client_id, message, local_connection):
    try:
        message_key, _ = message.split(b"|")
    except ValueError:  # message is bad, skip it
        return
    port = _options.redis_data_port
    if port == 0:
        client_id.sendall(
            protocol.message(
                protocol.REDIS_DATA_SERVER_FAILED,
                b"%s|Redis Data server is not started" % (message_key),
            )
        )
    else:
        if local_connection:
            port = _options.redis_data_socket
            host = "localhost"
        else:
            host = socket.gethostname()
        contents = b"%s|%s|%s" % (message_key, host.encode(), str(port).encode())
        client_id.sendall(protocol.message(protocol.REDIS_DATA_SERVER_OK, contents))


def _get_config_path(file_path: bytes) -> str:
    """The provided path should be a sub-path of `db_path`. It can be an absolute or
    relative path. Returns the absolute path."""
    file_path = os.path.expanduser(file_path.decode())
    root_path = _options.db_path
    if not file_path.startswith(root_path):
        # Make sure `file_path` is a relative path
        while file_path.startswith(os.sep):
            file_path = file_path[1:]
        file_path = os.path.join(_options.db_path, file_path)
    file_path = os.path.abspath(file_path)
    if ".." in os.path.relpath(file_path, _options.db_path):
        # Not allowed to access files above `db_path`
        raise PermissionError(file_path)
    return file_path


def _send_config_file(client_id, message):
    beacon_logger.debug("send_config_file %a", message)
    try:
        message_key, file_path = message.split(b"|")
    except ValueError:  # message is bad, skip it
        return
    file_path = _get_config_path(file_path)
    try:
        with open(file_path, "rb") as f:
            buffer = f.read()
            client_id.sendall(
                protocol.message(
                    protocol.CONFIG_GET_FILE_OK, b"%s|%s" % (message_key, buffer)
                )
            )
    except IOError:
        client_id.sendall(
            protocol.message(
                protocol.CONFIG_GET_FILE_FAILED,
                b"%s|File doesn't exist" % (message_key),
            )
        )


def _send_set_key(client_id: socket.socket, message: bytes):
    beacon_logger.debug("send_set_key %a", message)
    try:
        message_key, cmd_key, cmd_value = message.split(b"|", 2)
        key_name = cmd_key.decode("utf-8")
        value = cmd_value.decode("utf-8")
    except ValueError as e:
        client_id.sendall(
            protocol.message(
                protocol.KEY_SET_FAILED,
                b"%s|%s" % (message_key, e.args[0]),
            )
        )
        return
    _LOCAL_KEY_STORAGE[key_name] = value
    contents = b"%s" % (message_key)
    client_id.sendall(protocol.message(protocol.KEY_SET_OK, contents))


def _send_get_key(client_id: socket.socket, message: bytes):
    beacon_logger.debug("send_get_key %a", message)
    try:
        message_key, cmd_key = message.split(b"|", 1)
        key_name = cmd_key.decode("utf-8")
    except ValueError as e:
        client_id.sendall(
            protocol.message(
                protocol.KEY_GET_FAILED,
                b"%s|%s" % (message_key, e.args[0]),
            )
        )
        return
    value = _LOCAL_KEY_STORAGE.get(key_name, None)
    if value is None:
        client_id.sendall(
            protocol.message(
                protocol.KEY_GET_UNDEFINED,
                b"%s" % (message_key),
            )
        )
        return
    contents = b"%s|%s" % (message_key, value.encode("utf-8"))
    client_id.sendall(protocol.message(protocol.KEY_GET_OK, contents))


def __find_module(client_id, message_key, path, parent_name=None):
    for importer, name, ispkg in pkgutil.walk_packages([path]):
        module_name = name if parent_name is None else "%s.%s" % (parent_name, name)
        mdl = importer.find_module(name)
        if mdl is None:
            beacon_logger.warning("Module '%s' can't be imported", name)
            continue

        client_id.sendall(
            protocol.message(
                protocol.CONFIG_GET_PYTHON_MODULE_RX,
                b"%s|%s|%s"
                % (
                    message_key,
                    module_name.encode(),
                    mdl.get_filename().encode(),
                ),
            )
        )
        if ispkg:
            __find_module(client_id, message_key, os.path.join(path, name), module_name)


def _get_python_module(client_id, message):
    try:
        message_key, start_module_path = message.split(b"|")
    except ValueError:
        client_id.sendall(
            protocol.message(
                protocol.CONFIG_GET_PYTHON_MODULE_FAILED,
                b"%s|Can't split message (%s)" % (message_key, message),
            )
        )
        return

    start_module_path = _get_config_path(start_module_path)

    __find_module(client_id, message_key, start_module_path)
    client_id.sendall(
        protocol.message(protocol.CONFIG_GET_PYTHON_MODULE_END, b"%s|" % message_key)
    )


def __remove_empty_tree(base_dir=None, keep_empty_base=True):
    """
    Helper to remove empty directory tree.

    If *base_dir* is *None* (meaning start at the beacon server base directory),
    the *keep_empty_base* is forced to True to prevent the system from removing
    the beacon base path

    :param base_dir: directory to start from [default is None meaning start at
                     the beacon server base directory
    :type base_dir: str
    :param keep_empty_base: if True (default) doesn't remove the given
                            base directory. Otherwise the base directory is
                            removed if empty.
    """
    if base_dir is None:
        base_dir = _options.db_path
        keep_empty_base = False

    for dir_path, dir_names, file_names in os.walk(base_dir, topdown=False):
        if keep_empty_base and dir_path == base_dir:
            continue
        if file_names:
            continue
        for dir_name in dir_names:
            full_dir_name = os.path.join(dir_path, dir_name)
            if not os.listdir(full_dir_name):  # check if directory is empty
                os.removedirs(full_dir_name)


def _remove_config_file(client_id, message):
    try:
        message_key, file_path = message.split(b"|")
    except ValueError:  # message is bad, skip it
        return
    file_path = _get_config_path(file_path)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

        # walk back in directory tree removing empty directories. Do this to
        # prevent future rename operations to inadvertely ending up inside a
        # "transparent" directory instead of being renamed
        __remove_empty_tree()
        msg = (protocol.CONFIG_REMOVE_FILE_OK, b"%s|0" % (message_key,))
    except IOError:
        msg = (
            protocol.CONFIG_REMOVE_FILE_FAILED,
            b"%s|File/directory doesn't exist" % message_key,
        )
    else:
        event.send(None, "config_changed")

    client_id.sendall(protocol.message(*msg))


def _move_config_path(client_id, message):
    # should work on both files and folders
    # it can be used for both move and rename
    try:
        message_key, src_path, dst_path = message.split(b"|")
    except ValueError:  # message is bad, skip it
        return
    src_path = _get_config_path(src_path)
    dst_path = _get_config_path(dst_path)

    try:
        # make sure the parent directory exists
        parent_dir = os.path.dirname(dst_path)
        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)
        shutil.move(src_path, dst_path)

        # walk back in directory tree removing empty directories. Do this to
        # prevent future rename operations to inadvertely ending up inside a
        # "transparent" directory instead of being renamed
        __remove_empty_tree()
        msg = (protocol.CONFIG_MOVE_PATH_OK, b"%s|0" % (message_key,))
    except IOError as ioe:
        msg = (
            protocol.CONFIG_MOVE_PATH_FAILED,
            b"%s|%s: %s" % (message_key, ioe.filename, ioe.strerror),
        )
    else:
        event.send(None, "config_changed")
    client_id.sendall(protocol.message(*msg))


def _send_db_base_path(client_id, message):
    try:
        message_key, _ = message.split(b"|")
    except ValueError:
        return
    client_id.sendall(
        protocol.message(
            protocol.CONFIG_GET_DB_BASE_PATH_OK,
            bytes(f"{int(message_key)}|{_options.db_path}", "utf-8"),
        )
    )


def _send_config_db_files(client_id, message):
    beacon_logger.debug("send_config_db_files %a", message)
    try:
        message_key, path = message.split(b"|")
    except ValueError:  # message is bad, skip it
        return
    path = _get_config_path(path)
    yaml = YAML(pure=True)
    try:
        for root, dirs, files in os.walk(path, followlinks=True):
            try:
                files.remove("__init__.yml")
            except ValueError:  # init not in files list
                pass
            else:
                try:
                    with open(os.path.join(root, "__init__.yml"), "rt") as f:
                        yaml_content = yaml.load(f)
                    skipped_by_bliss = yaml_content.get("bliss_ignored", False)
                except (YAMLError, AttributeError):
                    skipped_by_bliss = False
                if skipped_by_bliss:
                    # This part of the resource tree was not provided for BLISS
                    beacon_logger.debug("Skip %s", root)
                    # Stop the recursive walk
                    dirs.clear()
                    continue
                files.insert(0, "__init__.yml")
            for filename in files:
                if filename.startswith("."):
                    continue
                basename, ext = os.path.splitext(filename)
                if ext == ".yml":
                    full_path = os.path.join(root, filename)
                    rel_path = full_path[len(_options.db_path) + 1 :]
                    try:
                        with codecs.open(full_path, "r", "utf-8") as f:
                            raw_buffer = f.read().encode("utf-8")
                            msg = protocol.message(
                                protocol.CONFIG_DB_FILE_RX,
                                b"%s|%s|%s"
                                % (message_key, rel_path.encode(), raw_buffer),
                            )
                            client_id.sendall(msg)
                    except Exception as e:
                        sys.excepthook(*sys.exc_info())
                        client_id.sendall(
                            protocol.message(
                                protocol.CONFIG_DB_FAILED,
                                b"%s|%s" % (message_key, repr(e).encode()),
                            )
                        )
    except Exception as e:
        sys.excepthook(*sys.exc_info())
        client_id.sendall(
            protocol.message(
                protocol.CONFIG_DB_FAILED, b"%s|%s" % (message_key, repr(e).encode())
            )
        )
    finally:
        client_id.sendall(
            protocol.message(protocol.CONFIG_DB_END, b"%s|" % (message_key))
        )


def __get_directory_structure(base_dir):
    """
    Helper that creates a nested dictionary that represents the folder structure of base_dir
    """
    result = {}
    base_dir = base_dir.rstrip(os.sep)
    start = base_dir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(base_dir, followlinks=True, topdown=True):
        # with topdown=True, the search can be pruned by altering 'dirs'
        dirs[:] = [d for d in dirs if d not in (".git",)]
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys((f for f in files if "~" not in f))
        parent = reduce(dict.get, folders[:-1], result)
        parent[folders[-1]] = subdir
    assert len(result) == 1
    return result.popitem()


def _send_config_db_tree(client_id, message):
    beacon_logger.debug("send_config_db_tree %a", message)
    try:
        message_key, look_path = message.split(b"|")
    except ValueError:  # message is bad, skip it
        return
    look_path = _get_config_path(look_path)
    try:
        _, tree = __get_directory_structure(look_path)
        msg = (
            protocol.CONFIG_GET_DB_TREE_OK,
            b"%s|%s" % (message_key, json.dumps(tree).encode()),
        )
    except Exception as e:
        sys.excepthook(*sys.exc_info())
        msg = (
            protocol.CONFIG_GET_DB_TREE_FAILED,
            b"%s|Failed to get tree: %s" % (message_key, str(e).encode()),
        )
    client_id.sendall(protocol.message(*msg))


def _write_config_db_file(client_id, message):
    first_pos = message.find(b"|")
    second_pos = message.find(b"|", first_pos + 1)

    if first_pos < 0 or second_pos < 0:  # message malformed
        msg = protocol.message(
            protocol.CONFIG_SET_DB_FILE_FAILED,
            b"%s|%s" % (message, "Malformed message"),
        )
        client_id.sendall(msg)
        return

    message_key = message[:first_pos]
    file_path = message[first_pos + 1 : second_pos]
    content = message[second_pos + 1 :]
    file_path = _get_config_path(file_path)
    file_dir = os.path.dirname(file_path)
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    try:
        with open(file_path, "wb") as f:
            f.write(content)
            msg = protocol.message(
                protocol.CONFIG_SET_DB_FILE_OK, b"%s|0" % message_key
            )
    except BaseException:
        msg = protocol.message(
            protocol.CONFIG_SET_DB_FILE_FAILED,
            b"%s|%s" % (message_key, traceback.format_exc().encode()),
        )
    else:
        event.send(None, "config_changed")
    client_id.sendall(msg)


def _send_uds_connection(client_id, client_hostname):
    client_hostname = client_hostname.decode()
    try:
        if uds_port_name and client_hostname == socket.gethostname():
            client_id.sendall(protocol.message(protocol.UDS_OK, uds_port_name.encode()))
        else:
            client_id.sendall(protocol.message(protocol.UDS_FAILED))
    except BaseException:
        sys.excepthook(*sys.exc_info())


def _get_set_client_id(client_id, messageType, message):
    message_key, message = message.split(b"|")
    if messageType is protocol.CLIENT_SET_NAME:
        _client_to_name[client_id] = message
    msg = b"%s|%s" % (message_key, _client_to_name.get(client_id, b""))
    client_id.sendall(protocol.message(protocol.CLIENT_NAME_OK, msg))


def _send_who_locked(client_id, message):
    message_key, *names = message.split(b"|")
    if not names:
        names = list(_lock_object.keys())

    for name in names:
        socket_id, compteur, lock_prio = _lock_object.get(name, (None, None, None))
        if socket_id is None:
            continue
        msg = b"%s|%s|%s" % (
            message_key,
            name,
            _client_to_name.get(socket_id, b"Unknown"),
        )
        client_id.sendall(protocol.message(protocol.WHO_LOCKED_RX, msg))
    client_id.sendall(protocol.message(protocol.WHO_LOCKED_END, b"%s|" % message_key))


def _send_log_server_address(client_id, message):
    message_key, *names = message.split(b"|")
    port = _options.log_server_port
    host = socket.gethostname().encode()
    if not port:
        # lo log server
        client_id.sendall(
            protocol.message(
                protocol.LOG_SERVER_ADDRESS_FAIL,
                b"%s|%s" % (message_key, b"no log server"),
            )
        )
    else:
        client_id.sendall(
            protocol.message(
                protocol.LOG_SERVER_ADDRESS_OK, b"%s|%s|%d" % (message_key, host, port)
            )
        )


def _send_unknow_message(client_id, message):
    client_id.sendall(protocol.message(protocol.UNKNOW_MESSAGE, message))


def _client_rx(client, local_connection):
    tcp_data = b""
    try:
        stopFlag = False
        while not stopFlag:
            try:
                raw_data = client.recv(16 * 1024)
            except BaseException:
                break

            if raw_data:
                tcp_data = b"%s%s" % (tcp_data, raw_data)
            else:
                break

            data = tcp_data
            c_id = client

            while data:
                try:
                    messageType, message, data = protocol.unpack_message(data)
                    if messageType == protocol.LOCK:
                        lock_objects = message.split(b"|")
                        prio = int(lock_objects.pop(0))
                        _lock(c_id, prio, lock_objects, message)
                    elif messageType == protocol.UNLOCK:
                        lock_objects = message.split(b"|")
                        prio = int(lock_objects.pop(0))
                        _unlock(c_id, prio, lock_objects)
                    elif messageType == protocol.LOCK_STOLEN_OK_REPLY:
                        client2sync = _waitstolen.get(message)
                        if client2sync is not None:
                            sync = client2sync.get(c_id)
                            if sync is not None:
                                sync.set()
                    elif messageType == protocol.REDIS_QUERY:
                        _send_redis_info(c_id, local_connection)
                    elif messageType == protocol.REDIS_DATA_SERVER_QUERY:
                        _send_redis_data_server_info(c_id, message, local_connection)
                    elif messageType == protocol.CONFIG_GET_FILE:
                        _send_config_file(c_id, message)
                    elif messageType == protocol.CONFIG_GET_DB_BASE_PATH:
                        _send_db_base_path(c_id, message)
                    elif messageType == protocol.CONFIG_GET_DB_FILES:
                        _send_config_db_files(c_id, message)
                    elif messageType == protocol.CONFIG_GET_DB_TREE:
                        _send_config_db_tree(c_id, message)
                    elif messageType == protocol.CONFIG_SET_DB_FILE:
                        _write_config_db_file(c_id, message)
                    elif messageType == protocol.CONFIG_REMOVE_FILE:
                        _remove_config_file(c_id, message)
                    elif messageType == protocol.CONFIG_MOVE_PATH:
                        _move_config_path(c_id, message)
                    elif messageType == protocol.CONFIG_GET_PYTHON_MODULE:
                        _get_python_module(c_id, message)
                    elif messageType == protocol.UDS_QUERY:
                        _send_uds_connection(c_id, message)
                    elif messageType == protocol.KEY_SET:
                        _send_set_key(c_id, message)
                    elif messageType == protocol.KEY_GET:
                        _send_get_key(c_id, message)
                    elif messageType in (
                        protocol.CLIENT_SET_NAME,
                        protocol.CLIENT_GET_NAME,
                    ):
                        _get_set_client_id(c_id, messageType, message)
                    elif messageType == protocol.WHO_LOCKED:
                        _send_who_locked(c_id, message)
                    elif messageType == protocol.LOG_SERVER_ADDRESS_QUERY:
                        _send_log_server_address(c_id, message)
                    else:
                        _send_unknow_message(c_id, message)
                except ValueError:
                    sys.excepthook(*sys.exc_info())
                    break
                except protocol.IncompleteMessage:
                    r, _, _ = select.select([client], [], [], 0.5)
                    if not r:  # if timeout, something wired, close the connection
                        data = None
                        stopFlag = True
                    break
                except BaseException:
                    sys.excepthook(*sys.exc_info())
                    beacon_logger.error("Error with client id %r, close it", client)
                    raise

            tcp_data = data
    except BaseException:
        sys.excepthook(*sys.exc_info())
    finally:
        try:
            _clean(client)
        finally:
            client.close()


@contextmanager
def pipe():
    rp, wp = os.pipe()
    try:
        yield (rp, wp)
    finally:
        os.close(wp)
        os.close(rp)


def log_tangodb_started():
    """Raise exception when tango database not started in 10 seconds"""
    from bliss.tango.clients.utils import wait_tango_db

    try:
        wait_tango_db(port=_options.tango_port, db=2)
    except Exception:
        tango_logger.error("Tango database NOT started")
        raise
    else:
        tango_logger.info("Tango database started")


@contextmanager
def start_tcp_server():
    """Part of the 'Beacon server'"""
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        tcp.bind(("", _options.port))
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            raise RuntimeError(f"Port {_options.port} already in use") from e
        else:
            raise e
    tcp.listen(512)  # limit to 512 clients
    try:
        yield tcp
    finally:
        tcp.close()


@contextmanager
def start_uds_server():
    """Part of the 'Beacon server'"""
    global uds_port_name
    if IS_WINDOWS:
        uds_port_name = None
        yield None
        return
    path = tempfile._get_default_tempdir()
    random_name = next(tempfile._get_candidate_names())
    uds_port_name = os.path.join(path, f"beacon_{random_name}.sock")
    try:
        uds = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        uds.bind(uds_port_name)
        os.chmod(uds_port_name, 0o777)
        uds.listen(512)
        try:
            yield uds
        finally:
            uds.close()
    finally:
        try:
            os.unlink(uds_port_name)
        except Exception:
            pass


def tcp_server_main(sock):
    """Beacon server: listen on TCP port"""
    port = sock.getsockname()[1]
    beacon_logger.info("start listening on TCP port %s", port)
    beacon_logger.info("configuration path: %s", _options.db_path)
    try:
        while True:
            try:
                newSocket, addr = sock.accept()
            except cancel_wait_ex:
                return
            if platform.system() != "Windows":
                newSocket.setsockopt(socket.SOL_IP, socket.IP_TOS, 0x10)
            localhost = addr[0] == "127.0.0.1"
            gevent.spawn(_client_rx, newSocket, localhost)
    finally:
        beacon_logger.info("stop listening on TCP port %s", port)


def ensure_global_beacon_connection(beacon_port):
    """Avoid auto-discovery of port for the global connection object."""
    if client_utils._default_connection is None:
        client_utils._default_connection = connection_utils.Connection(
            "localhost", beacon_port
        )


def uds_server_main(sock):
    """Beacon server: listen on UDS socket"""
    beacon_logger.info("start listening on UDS socket %s", uds_port_name)
    try:
        while True:
            try:
                newSocket, addr = sock.accept()
            except cancel_wait_ex:
                return
            gevent.spawn(_client_rx, newSocket, True)
    finally:
        beacon_logger.info("stop listening on UDS socket %s", uds_port_name)


def stream_to_log(stream, log_func):
    """Forward a stream to a log function"""
    gevent.get_hub().threadpool.maxsize += 1
    while True:
        msg = gevent.os.tp_read(stream, 8192)
        if msg:
            log_func(msg.decode())


@contextmanager
def logged_subprocess(args, logger, **kw):
    """Subprocess with stdout/stderr logging"""
    with pipe() as (rp_out, wp_out):
        with pipe() as (rp_err, wp_err):
            log_stdout = gevent.spawn(stream_to_log, rp_out, logger.info)
            log_stderr = gevent.spawn(stream_to_log, rp_err, logger.error)
            greenlets = [log_stdout, log_stderr]
            proc = subprocess.Popen(args, stdout=wp_out, stderr=wp_err, **kw)
            msg = f"(pid={proc.pid}) {repr(' '.join(args))}"
            beacon_logger.info(f"started {msg}")
            try:
                yield proc
            finally:
                beacon_logger.info(f"terminating {msg}")
                proc.terminate()
                gevent.killall(greenlets)
                beacon_logger.info(f"terminated {msg}")


@contextmanager
def spawn_context(func, *args, **kw):
    g = gevent.spawn(func, *args, **kw)
    try:
        yield
    finally:
        g.kill()


def wait():
    """Wait for exit signal"""

    with pipe() as (rp, wp):

        def sigterm_handler(*args, **kw):
            # This is executed in the hub so use a pipe
            # Find a better way:
            # https://github.com/gevent/gevent/issues/1683
            os.write(wp, b"!")

        event = gevent.event.Event()

        def sigterm_greenlet():
            # Graceful shutdown
            gevent.get_hub().threadpool.maxsize += 1
            gevent.os.tp_read(rp, 1)
            beacon_logger.info("Received a termination signal")
            event.set()

        with spawn_context(sigterm_greenlet):
            # Binds system signals.
            signal.signal(signal.SIGTERM, sigterm_handler)
            if IS_WINDOWS:
                signal.signal(signal.SIGINT, sigterm_handler)
                # ONLY FOR Win7 (COULD BE IGNORED ON Win10 WHERE CTRL-C PRODUCES A SIGINT)
                win32api.SetConsoleCtrlHandler(sigterm_handler, True)
            else:
                signal.signal(signal.SIGHUP, sigterm_handler)
                signal.signal(signal.SIGQUIT, sigterm_handler)

            try:
                event.wait()
            except KeyboardInterrupt:
                beacon_logger.info("Received a keyboard interrupt")
            except Exception as exc:
                sys.excepthook(*sys.exc_info())
                beacon_logger.critical("An unexpected exception occurred:\n%r", exc)


def configure_logging():
    """Configure the root logger:

    - set log level according to CLI arguments
    - send DEBUG and INFO to STDOUT
    - send WARNING, ERROR and CRITICAL to STDERR
    """
    log_fmt = "%(levelname)s %(asctime)-15s %(name)s: %(message)s"

    rootlogger = logging.getLogger()
    rootlogger.setLevel(_options.log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(lambda record: record.levelno < logging.WARNING)
    handler.setFormatter(logging.Formatter(log_fmt))
    rootlogger.addHandler(handler)

    handler = logging.StreamHandler(sys.stderr)
    handler.addFilter(lambda record: record.levelno >= logging.WARNING)
    handler.setFormatter(logging.Formatter(log_fmt))
    rootlogger.addHandler(handler)


def launch_redis_server(
    context_stack,
    logger,
    cwd,
    config_file,
    port,
    unixsocket=None,
    timeout=3,
    plugins=[],
):
    proc_args = ["redis-server", config_file, "--port", str(port)]
    if not IS_WINDOWS and unixsocket is not None:
        proc_args += [
            "--unixsocket",
            unixsocket,
            "--unixsocketperm",
            "777",
        ]
        redis_url = f"unix://{unixsocket}"
    else:
        redis_url = f"redis://{socket.gethostname()}:{port}"

    for plugin_path in plugins:
        if os.path.isfile(plugin_path):
            proc_args += ["--loadmodule", plugin_path]
        else:
            raise Exception(f"Redis server plugin not found: {plugin_path}")

    ctx = logged_subprocess(proc_args, logger, cwd=cwd)
    proc = context_stack.enter_context(ctx)

    for _ in range(int(10 * timeout)):
        try:
            red = redis.Redis.from_url(redis_url)
            redis_pid = red.info()["process_id"]
            if redis_pid != proc.pid:
                raise Exception(
                    f"'{redis_url}' already used by another redis-server (PID:{redis_pid})"
                )
            break
        except redis.exceptions.ConnectionError:
            time.sleep(0.1)
    else:
        raise Exception(
            f"Failed to start Redis server, '{redis_url}' not reachable after {timeout} seconds."
        )

    return redis_url


def key_value(key: str) -> list[str]:
    """Extra key exposed by Beacon.

    Have to be in `KEY=VALUE` format
    """
    res = key.split("=", 1)
    if len(res) != 2:
        raise ValueError(f"'{key}' is not a valid KEY=VALUE sequence")
    return res


def main(args=None):
    # Monkey patch needed for web server
    # just keep for consistency because it's already patched
    # in __init__ in bliss project
    from gevent import monkey

    monkey.patch_all(thread=False)

    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db-path",
        "--db_path",
        dest="db_path",
        default=os.environ.get("BEACON_DB_PATH", "./db"),
        help="database path",
    )
    parser.add_argument(
        "--redis-port",
        "--redis_port",
        dest="redis_port",
        default=6379,
        type=int,
        help="redis connection port",
    )
    parser.add_argument(
        "--redis-conf",
        "--redis_conf",
        dest="redis_conf",
        default=redis_conf.get_redis_config_path(),
        help="path to alternative redis configuration file",
    )
    parser.add_argument(
        "--redis-data-port",
        "--redis_data_port",
        dest="redis_data_port",
        default=6380,
        type=int,
        help="redis data connection port (0 mean don't start redis data server)",
    )
    parser.add_argument(
        "--redis-data-conf",
        "--redis_data_conf",
        dest="redis_data_conf",
        default=redis_conf.get_redis_data_config_path(),
        help="path to alternative redis configuration file for data server",
    )
    parser.add_argument(
        "--redis-data-socket",
        dest="redis_data_socket",
        default="/tmp/redis_data.sock",
        help="Unix socket for redis (default to /tmp/redis_data.sock)",
    )
    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=int(os.environ.get("BEACON_PORT", 25000)),
        help="server port (default to BEACON_PORT environment variable, "
        "otherwise 25000)",
    )
    parser.add_argument(
        "--tango-port",
        "--tango_port",
        dest="tango_port",
        type=int,
        default=0,
        help="tango server port (default to 0: disable)",
    )
    parser.add_argument(
        "--tango-debug-level",
        "--tango_debug_level",
        dest="tango_debug_level",
        type=int,
        default=0,
        help="tango debug level (default to 0: WARNING,1:INFO,2:DEBUG)",
    )
    parser.add_argument(
        "--webapp-port",
        "--webapp_port",
        dest="webapp_port",
        type=int,
        default=9030,
        help="DEPRECATED: Configuration page no more uses a dedicated port. "
        "Use http://<hostname>:<homepage_port>/config instead.",
    )
    parser.add_argument(
        "--homepage-port",
        "--homepage_port",
        dest="homepage_port",
        type=int,
        default=9010,
        help="web port for the homepage (0: disable)",
    )
    parser.add_argument(
        "--log-server-port",
        "--log_server_port",
        dest="log_server_port",
        type=int,
        default=9020,
        help="logger server port (0: disable)",
    )
    parser.add_argument(
        "--log-output-folder",
        "--log_output_folder",
        dest="log_output_folder",
        type=str,
        default="/var/log/bliss",
        help="logger output folder (default is /var/log/bliss)",
    )
    parser.add_argument(
        "--log-size",
        "--log_size",
        dest="log_size",
        type=float,
        default=10,
        help="Size of log rotating file in MegaBytes (default is 10)",
    )
    parser.add_argument(
        "--log-viewer-port",
        "--log_viewer_port",
        dest="log_viewer_port",
        type=int,
        default=9080,
        help="Web port for the log viewer socket (0: disable)",
    )
    parser.add_argument(
        "--redis-socket",
        "--redis_socket",
        dest="redis_socket",
        default="/tmp/redis.sock",
        help="Unix socket for redis (default to /tmp/redis.sock)",
    )
    parser.add_argument(
        "--log-level",
        "--log_level",
        default="INFO",
        type=str,
        choices=["DEBUG", "INFO", "WARN", "ERROR"],
        help="log level",
    )
    parser.add_argument(
        "--key",
        metavar="KEY=VALUE",
        dest="keys",
        default=[],
        type=key_value,
        action="append",
        help="Exported key from the Beacon service",
    )

    global _options
    _options = parser.parse_args(args)

    # Pimp my path
    _options.db_path = os.path.abspath(os.path.expanduser(_options.db_path))

    # Feed the key-value database
    for k in _options.keys:
        _LOCAL_KEY_STORAGE[k[0]] = k[1]

    # Logging configuration
    configure_logging()

    with ExitStack() as context_stack:
        # For sub-processes
        env = dict(os.environ)

        # Start the Beacon server
        ctx = start_tcp_server()
        tcp_socket = context_stack.enter_context(ctx)
        ctx = start_uds_server()
        uds_socket = context_stack.enter_context(ctx)
        beacon_port = tcp_socket.getsockname()[1]
        env["BEACON_HOST"] = "%s:%d" % ("localhost", beacon_port)

        # Logger server application
        if _options.log_server_port > 0:
            # Logserver executable
            args = [sys.executable]
            args += ["-m", "bliss.config.conductor.log_server"]

            # Arguments
            args += ["--port", str(_options.log_server_port)]
            if not _options.log_output_folder:
                log_folder = os.path.join(str(_options.db_path), "logs")
            else:
                log_folder = str(_options.log_output_folder)

            # Start log server when the log folder is writeable
            if os.access(log_folder, os.R_OK | os.W_OK | os.X_OK):
                args += ["--log-output-folder", log_folder]
                args += ["--log-size", str(_options.log_size)]
                beacon_logger.info(
                    "launching log_server on port: %s", _options.log_server_port
                )
                ctx = logged_subprocess(args, log_server_logger, env=env)
                context_stack.enter_context(ctx)

                # Logviewer Web application
                if not IS_WINDOWS and _options.log_viewer_port > 0:
                    args = ["tailon"]
                    args += ["-b", f"0.0.0.0:{_options.log_viewer_port}"]
                    args += [os.path.join(_options.log_output_folder, "*")]
                    ctx = logged_subprocess(args, log_viewer_logger, env=env)
                    context_stack.enter_context(ctx)
            else:
                raise RuntimeError(
                    f"Log path {log_folder} does not exist."
                    " Please create it or specify another one with --log-output-folder option"
                )

        # Start redis server(s)

        # determine RediSearch and RedisJSON library paths
        librejson = os.path.join(env.get("CONDA_PREFIX", "/usr"), "lib", "librejson.so")
        redisearch = os.path.join(
            env.get("CONDA_PREFIX", "/usr"), "lib", "redisearch.so"
        )

        launch_redis_server(
            context_stack,
            redis_logger,
            _options.db_path,
            _options.redis_conf,
            _options.redis_port,
            _options.redis_socket,
            plugins=[librejson, redisearch],
        )

        if _options.redis_data_port > 0:
            redis_data_url = launch_redis_server(
                context_stack,
                redis_data_logger,
                _options.db_path,
                _options.redis_data_conf,
                _options.redis_data_port,
                _options.redis_data_socket,
                plugins=[librejson, redisearch],
            )

            # Apply blissdata setup on the fresh Redis database
            _ = DataStore(redis_data_url, init_db=True)

            redis_data_protected_history = 180
            redis_data_tracker = [
                "memory_tracker",
                "--redis-url",
                redis_data_url,
                "--protected-history",
                str(redis_data_protected_history),
            ]
            ctx = logged_subprocess(redis_data_tracker, memory_tracker_logger)
            context_stack.enter_context(ctx)

        # Start Tango database
        if _options.tango_port > 0:
            # Tango database executable
            args = ["NosqlTangoDB"]

            # Arguments
            args += ["-l", str(_options.tango_debug_level)]
            args += ["--db_access", "beacon"]
            args += ["--port", str(_options.tango_port)]
            args += ["2"]

            # Start tango database
            ctx = logged_subprocess(args, tango_logger, env=env)
            context_stack.enter_context(ctx)
            ctx = spawn_context(log_tangodb_started)
            context_stack.enter_context(ctx)

        # Start processing Beacon requests
        if uds_socket is not None:
            ctx = spawn_context(uds_server_main, uds_socket)
            context_stack.enter_context(ctx)
        if tcp_socket is not None:
            ctx = spawn_context(tcp_server_main, tcp_socket)
            context_stack.enter_context(ctx)

        ensure_global_beacon_connection(beacon_port)

        # run the web server for homepage, config and RestAPI apps
        app = create_app(_options.log_viewer_port)
        http_server = WSGIServer(("0.0.0.0", _options.homepage_port), app)
        ctx = spawn_context(http_server.serve_forever)
        context_stack.enter_context(ctx)
        web_logger.info(
            f"Web server ready at {socket.gethostname()}:{_options.homepage_port}"
        )

        # Still create a server to listen on deprecated webapp_port to inform users with new URL.
        # This could be completely removed after some time
        redirect_app = flask.Flask(__name__)

        @redirect_app.route("/", defaults={"path": ""})
        @redirect_app.route("/<path:path>")
        def catch_all(path):
            url = f"http://{flask.request.server[0]}:{_options.homepage_port}/config"
            response = f"<h1 style='text-align: center;''>{'<p>&nbsp;</p>'*3}<strong>Configuration page has moved...</strong></h1>"
            response += f"<h2 style='text-align: center;''>Please use <a href='{url}''>{url}</a> instead.</h2>"
            response += "<p style='text-align: center;''><em>(port number can be omitted on ESRF beamlines)</em></p>"
            return response

        redirect_server = WSGIServer(("0.0.0.0", _options.webapp_port), redirect_app)
        ctx = spawn_context(redirect_server.serve_forever)
        context_stack.enter_context(ctx)

        # Wait for exit signal
        wait()


if __name__ == "__main__":
    main()
