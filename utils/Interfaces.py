import threading
import PySide2.QtCore


class IVariable(object):

    def __init__(self, name=None, value=None, row=None, col=None, type=None, protected=False):
        self.name = name
        self.value = value
        self.row = row
        self.col = col
        self.type = type
        self.protected = protected


class IVariables(PySide2.QtCore.QObject):

    signal_set = PySide2.QtCore.Signal(str, IVariable)
    singelton = {}
    lock = threading.Lock()

    def __init__(self, parent=None):
        PySide2.QtCore.QObject.__init__(self, parent)

    def set(self, name, value):

        IVariables.lock.acquire()
        try:

            if name in self.__dict__.keys():
                if isinstance(self.__dict__[name], IVariable):
                    self.__dict__[name].value = self.__dict__[name].type(value)

            self.signal_set.emit(name, self.__dict__[name])

        finally:
            IVariables.lock.release()

    def get(self, name):

        IVariables.lock.acquire()
        try:

            if name in self.__dict__.keys():
                if isinstance(self.__dict__[name], IVariable):
                    _return = self.__dict__[name].type(self.__dict__[name].value)
        finally:
            IVariables.lock.release()

        return _return

    def emit_all(self):

        for name in self.__dict__.keys():
            if isinstance(self.__dict__[name], IVariable):
                self.signal_set.emit(name, self.__dict__[name])
