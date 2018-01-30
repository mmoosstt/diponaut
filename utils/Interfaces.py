import threading
import PySide.QtCore


class IVariables(object):

    singelton = None
    lock = threading.Lock()

    @staticmethod
    def getInterface():
        if IVariables.singelton:
            return IVariables.singelton
        else:
            IVariables()
            return IVariables.singelton

    def __init__(self):
        if IVariables.singelton == None:
            IVariables.singelton = self

    def set(self, name, value):

        IVariables.lock.acquire()
        try:
            if name in IVariables.singelton.__dict__.keys():
                IVariables.singelton.__dict__[name] = value

        finally:
            IVariables.lock.release()

    def get(self, name):

        IVariables.lock.acquire()
        try:
            if name in IVariables.singelton.__dict__.keys():
                _return = IVariables.singelton.__dict__[name]

        finally:
            IVariables.lock.release()

        return _return
