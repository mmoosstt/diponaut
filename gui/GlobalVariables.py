import PySide
import PySide.QtGui
import PySide.QtCore
import logic.DataApi
import utils.Interfaces


class myLineEdit(PySide.QtGui.QLineEdit):

    valueChanged = PySide.QtCore.Signal(str, object)

    def __init__(self, parent, name):
        PySide.QtGui.QLineEdit.__init__(self, parent)
        self.name = name

        self.textChanged.connect(self.myTextChanged)

    def myTextChanged(self, value):
        self.value = value
        self.textChanged.disconnect(self.myTextChanged)
        self.valueChanged.emit(self.name, self.value)
        self.textChanged.connect(self.myTextChanged)


class GlobalVariables(PySide.QtGui.QWidget):

    def __init__(self, parent=None):
        PySide.QtGui.QWidget.__init__(self, parent)

        self.data_state = None
        self.data_prediction = None
        self.GloVar = logic.DataApi.GloVar
        self.GloVar.signal_set.connect(self.SetGloValues)

        layout = PySide.QtGui.QGridLayout(self)

        row = 0
        col = 0

        for _name in sorted(self.GloVar.__dict__.keys()):
            _obj = self.GloVar.__dict__[_name]
            if isinstance(_obj, utils.Interfaces.IVariable):

                print(_obj.type, _name)
                layout.addWidget(PySide.QtGui.QLabel(_name, self), row, col)
                self.__dict__["Q{0}".format(_name)] = myLineEdit(self, _name)
                layout.addWidget(self.__dict__["Q{0}".format(_name)], row, col + 1)
                self.__dict__["C{0}".format(_name)] = lambda name, value: self.GloVar.set(name, value)
                self.__dict__["Q{0}".format(_name)].valueChanged.connect(self.__dict__["C{0}".format(_name)])
                row += 1

        self.setLayout(layout)

    def SetGloValues(self, name, value):

        _attrib_str = "Q{0}".format(name)
        _callback_str = "C{0}".format(name)

        if _attrib_str in self.__dict__.keys():
            _object = self.__dict__[_attrib_str]
            _callback = self.__dict__[_callback_str]

            if isinstance(_object, PySide.QtGui.QLineEdit):
                _object.valueChanged.disconnect(_callback)
                _object.setText(str(value))
                _object.valueChanged.connect(_callback)

    def SetDataStates(self, Data):

        if isinstance(Data, DataApi.TradingStates):
            self.data_state = Data

    def SetDataPrediction(self, Data):

        if isinstance(Data, DataApi.TradingPrediction):
            self.dataPrediction = Data


if __name__ == "__main__":
    app = PySide.QtGui.QApplication([])

    MainWidget = TraidingInterface()
    MainWidget.resize(800, 800)
    MainWidget.show()
    app.exec_()
