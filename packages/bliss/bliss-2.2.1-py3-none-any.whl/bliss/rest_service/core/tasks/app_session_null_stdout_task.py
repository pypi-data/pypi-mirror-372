# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import gevent
from prompt_toolkit.application import current
from prompt_toolkit.application import AppSession
from prompt_toolkit.output import DummyOutput

from .task import Task
from .proxy_task import ProxyTask


class AppSessionNullStdoutTask(ProxyTask):
    """
    Setup a dedicated app session to the coroutine in order to not print
    stdout in the screen.
    """

    def __init__(self, task: Task):
        ProxyTask.__init__(self, task)

    def __call__(self, *args, **kwargs):
        dummy_output = DummyOutput()
        app_session = AppSession(None, dummy_output)
        current._current_app_session.set(app_session)
        g = gevent.getcurrent()
        g.spawn_tree_locals["app_session"] = app_session
        result = self._task(*args, **kwargs)
        return result
