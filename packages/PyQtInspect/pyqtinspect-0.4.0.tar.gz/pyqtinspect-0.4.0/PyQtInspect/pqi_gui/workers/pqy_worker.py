# -*- encoding:utf-8 -*-
import sys
from PyQt5 import QtCore
import traceback
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR

from PyQtInspect._pqi_bundle.pqi_typing import OptionalDict
from PyQtInspect.pqi_gui.workers.dispatcher import Dispatcher


class PQYWorker(QtCore.QObject):
    sigWidgetInfoRecv = QtCore.pyqtSignal(dict)
    sigNewDispatcher = QtCore.pyqtSignal(Dispatcher)
    sigDispatcherExited = QtCore.pyqtSignal(int)
    sigAllDispatchersExited = QtCore.pyqtSignal()
    sigSocketError = QtCore.pyqtSignal(str)

    def __init__(self, parent, port):
        super().__init__(parent)
        self.port = port

        self.dispatchers = []  # type: list[Dispatcher]
        self.idToDispatcher = {}  # type: dict[int, Dispatcher]

        self._isServing = False
        self._socket = None

    def run(self):
        self._isServing = True
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.settimeout(None)

        try:
            from socket import SO_REUSEPORT
            self._socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        except ImportError:
            self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            self._socket.bind(('', self.port))
            self._socket.listen(1)

            dispatcherId = 0

            while self._isServing:
                newSock, _addr = self._socket.accept()
                # Create a new thread to handle the connection.
                dispatcher = Dispatcher(None, newSock, dispatcherId)
                # The connection type must be DirectConnection,
                # otherwise the signal will be ignored because the thread event loop is not running.
                dispatcher.sigClosed.connect(self._onDispatcherClosed, QtCore.Qt.DirectConnection)
                self.dispatchers.append(dispatcher)
                self.idToDispatcher[dispatcherId] = dispatcher

                self.sigNewDispatcher.emit(dispatcher)
                dispatcher.start()
                dispatcherId += 1

        except Exception as e:
            if not self._isServing or getattr(e, 'errno') == 10038:
                return  # Socket closed.

            sys.stderr.write("Could not bind to port: %s\n" % (self.port,))
            sys.stderr.flush()
            traceback.print_exc()
            self.sigSocketError.emit(str(e))

    def stop(self):
        self._isServing = False
        for dispatcher in self.dispatchers:
            dispatcher.close()

        if self._socket:
            # ---
            # For linux, we need to shut down the socket before close it.
            # Otherwise, the socket will be in TIME_WAIT state and block program.
            # ---
            try:
                self._socket.shutdown(SHUT_RDWR)
            except:
                # ---
                # Fixed 20240820: Ignore the exception when shutdown the socket in macOS.
                # ---
                pass
            self._socket.close()

    def onMsg(self, info: dict):
        self.sigWidgetInfoRecv.emit(info)

    def sendEnableInspect(self, extra: dict):
        for dispatcher in self.dispatchers:
            dispatcher.sendEnableInspect(extra)

    def sendEnableInspectToDispatcher(self, dispatcherId: int, extra: dict):
        dispatcher = self.idToDispatcher.get(dispatcherId)
        if dispatcher:
            dispatcher.sendEnableInspect(extra)

    def sendDisableInspect(self):
        for dispatcher in self.dispatchers:
            dispatcher.sendDisableInspect()

    def sendExecCodeEvent(self, dispatcherId: int, code: str):
        dispatcher = self.idToDispatcher.get(dispatcherId)
        if dispatcher:
            dispatcher.sendExecCodeEvent(code)

    def sendHighlightWidgetEvent(self, dispatcherId: int, widgetId: int, isHighlight: bool):
        dispatcher = self.idToDispatcher.get(dispatcherId)
        if dispatcher:
            dispatcher.sendHighlightWidgetEvent(widgetId, isHighlight)

    def sendSelectWidgetEvent(self, dispatcherId: int, widgetId: int):
        dispatcher = self.idToDispatcher.get(dispatcherId)
        if dispatcher:
            dispatcher.sendSelectWidgetEvent(widgetId)

    def sendRequestWidgetInfoEvent(self, dispatcherId: int, widgetId: int, extra: OptionalDict = None):
        dispatcher = self.idToDispatcher.get(dispatcherId)
        if dispatcher:
            dispatcher.sendRequestWidgetInfoEvent(widgetId, extra)

    def sendRequestChildrenInfoEvent(self, dispatcherId: int, widgetId: int):
        dispatcher = self.idToDispatcher.get(dispatcherId)
        if dispatcher:
            dispatcher.sendRequestChildrenInfoEvent(widgetId)

    def sendRequestControlTreeInfoEvent(self, dispatcherId: int, extra: OptionalDict = None):
        dispatcher = self.idToDispatcher.get(dispatcherId)
        if dispatcher:
            dispatcher.sendRequestControlTreeInfoEvent(extra)

    def sendRequestWidgetPropsEvent(self, dispatcherId: int, widgetId: int):
        dispatcher = self.idToDispatcher.get(dispatcherId)
        if dispatcher:
            dispatcher.sendRequestWidgetPropsEvent(widgetId)

    def _onDispatcherClosed(self, id: int):
        try:
            dispatcher = self.idToDispatcher.pop(id)
            self.dispatchers.remove(dispatcher)
            dispatcher.deleteLater()
            # emit once
            self.sigDispatcherExited.emit(id)
        except KeyError:  # may be already removed.
            pass

        if not self.dispatchers:
            self.sigAllDispatchersExited.emit()


class DummyWorker:
    def __getattr__(self, item):
        return lambda *args, **kwargs: None

    def __bool__(self):
        return False


DUMMY_WORKER = DummyWorker()
