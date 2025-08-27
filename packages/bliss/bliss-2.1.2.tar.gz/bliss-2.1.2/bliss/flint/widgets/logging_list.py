# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Provide a widget to display logs from `logging` Python module.
"""

from __future__ import annotations

import sys
import logging
import functools
import weakref

from silx.gui import qt

from bliss.flint.model import logging_model
from .logging_widgets import colorFromLevel


class LoggingList(qt.QTreeView):
    """Display messages from the Python logging system.

    By default only the 100 last messages are displayed. This can be customed
    using the method `setMaximumLogCount`
    """

    DateTimeColumn = 0
    LevelColumn = 1
    ModuleNameColumn = 2
    MessageColumn = 3

    RecordRole = qt.Qt.UserRole + 1

    logSelected = qt.Signal(str)
    """Emitted when a log record was selected

    The event contain the name of the logger.
    """

    def __init__(self, parent=None):
        super(LoggingList, self).__init__(parent=parent)
        self.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.setWordWrap(True)
        self.setTextElideMode(qt.Qt.ElideRight)

        self._handlers: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
        self.destroyed.connect(functools.partial(self._remove_handlers, self._handlers))
        self._formatter = logging.Formatter()
        self._records: list[logging_model.SealedLogRecord] = []

        self.__logModel: logging_model.LoggingModel | None = None

        self._timer = qt.QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self.flushRecords)
        self._timer.start()

        model = qt.QStandardItemModel(self)
        model.setColumnCount(4)
        model.setHorizontalHeaderLabels(["Date/time", "Level", "Module", "Message"])
        self.setModel(model)

        selectionModel = self.selectionModel()
        selectionModel.currentRowChanged.connect(self.__currentRowChanged)

        self.setAlternatingRowColors(True)

        # It could be very big cells so per pixel is better
        self.setVerticalScrollMode(qt.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(qt.QAbstractItemView.ScrollPerPixel)

        header = self.header()
        header.setSectionResizeMode(
            self.DateTimeColumn, qt.QHeaderView.ResizeToContents
        )
        header.setSectionResizeMode(self.LevelColumn, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            self.ModuleNameColumn, qt.QHeaderView.ResizeToContents
        )
        header.setSectionResizeMode(self.MessageColumn, qt.QHeaderView.Stretch)

    def setLogModel(self, model: logging_model.LoggingModel | None):
        if self.__logModel is not None:
            self.__logModel.recordReceived.disconnect(self.appendRecord)
        self.__logModel = model
        if model is not None:
            self._records += model.records()
            model.recordReceived.connect(self.appendRecord)

    def logModel(self) -> logging_model.LoggingModel | None:
        return self.__logModel

    def __currentRowChanged(self, current: qt.QModelIndex, previous: qt.QModelIndex):
        if current.parent() == qt.QModelIndex():
            model = self.model()
            i = model.index(current.row(), 2)
            name = model.data(i)
            self.logSelected.emit(name)

    @staticmethod
    def _remove_handlers(handlers):
        # NOTE: This function have to be static to avoid cyclic reference to the widget
        #       in the destroyed signal
        for handler, logger in handlers.items():
            logger.removeHandler(handler)
        handlers.clear()

    def logCount(self):
        """
        Returns the amount of log messages displayed.
        """
        return self.model().rowCount()

    def _formatStack(self, record: logging_model.SealedLogRecord):
        s = ""
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self._formatter.formatException(record.exc_info)
        if record.exc_text:
            s = record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self._formatter.formatStack(record.stack_info)
        return s

    def __splitCauses(self, stack):
        """Split a traceback into different causes

        It looks like the record object do not provide anymore always access to
        individual exceptions. So we have to parse it.
        """
        line = "The above exception was the direct cause of the following exception:"
        causes = stack.split(line)
        causes = [c.strip() for c in causes]
        return list(reversed(causes))

    def appendRecord(self, record: logging_model.SealedLogRecord):
        """Add a record to the widget.

        The update of the display is done asynchronously
        """
        self._records.append(record)

    def flushRecords(self):
        records = self._records
        if records == []:
            return
        self._records = []
        # FIXME: Some could drop records if more than _maximumLogCount
        self.addRecords(records)

    def addRecords(self, records: list[logging_model.SealedLogRecord]):
        if self.__logModel is None:
            # NOTE: Here we can't log anything because it's part of the logging handler
            print("No logging model")
            return
        scroll = self.verticalScrollBar()
        makeLastVisible = scroll.value() == scroll.maximum()

        for record in records:
            self.__displayRecord(record)

        model: qt.QStandardItemModel = self.model()
        maxLogs = self.__logModel.maximumLogCount()
        if model.rowCount() > maxLogs:
            count = model.rowCount() - maxLogs
            # Always remove an even amount of items to avoid blinking with alternatingRowColorswith
            count += count % 2
            model.removeRows(0, count)

        if makeLastVisible:
            self.scrollToBottom()

    def recordFromIndex(
        self, index: qt.QModelIndex
    ) -> logging_model.SealedLogRecord | None:
        if index.parent() != qt.QModelIndex():
            return None
        m = self.model()
        i = m.index(index.row(), self.DateTimeColumn)
        record = m.data(i, self.RecordRole)
        return record

    def __displayRecord(self, record: logging_model.SealedLogRecord):
        message = record.getMessage()
        dateTimeItem = None
        try:
            dt = self._formatter.formatTime(record)
            dateTimeItem = qt.QStandardItem(dt)
            dateTimeItem.setData(record, self.RecordRole)
            levelItem = qt.QStandardItem(record.levelname)
            levelno = record.levelno
            color = colorFromLevel(levelno, 128)
            levelItem.setBackground(color)
            nameItem = qt.QStandardItem(record.name)
            messageItem = qt.QStandardItem(message)

            stack = self._formatStack(record)
            if stack != "":
                causes = self.__splitCauses(stack)
                parentItem = dateTimeItem
                for i, cause in enumerate(causes):
                    title = qt.QStandardItem("Backtrace" if i == 0 else "Caused by")
                    parentItem.appendRow(
                        [
                            title,
                            qt.QStandardItem(),
                            qt.QStandardItem(),
                            qt.QStandardItem(cause),
                        ]
                    )
                    parentItem = title
        except Exception:
            # Make sure everything is fine
            sys.excepthook(*sys.exc_info())

        if dateTimeItem is None:
            dateTimeItem = qt.QStandardItem()
            levelItem = qt.QStandardItem("CRITICAL")
            levelno = logging.CRITICAL
            color = colorFromLevel(levelno, 128)
            levelItem.setBackground(color)
            nameItem = qt.QStandardItem()
            messageItem = qt.QStandardItem(message)

        model: qt.QStandardItemModel = self.model()
        model.appendRow([dateTimeItem, levelItem, nameItem, messageItem])
