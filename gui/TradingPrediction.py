import PySide
import PySide.QtGui
import PySide.QtCore
from logic.DataApi import GloVar


class TraidingInterface(PySide.QtGui.QWidget):

    def __init__(self, parent=None):
        PySide.QtGui.QWidget.__init__(self, parent)

        self.data_state = None
        self.data_prediction = None

        layout = PySide.QtGui.QGridLayout(self)

        # header 1
        layout.addWidget(PySide.QtGui.QLabel("     ", self), 0, 0)
        layout.addWidget(PySide.QtGui.QLabel("price", self), 0, 1)
        layout.addWidget(PySide.QtGui.QLabel("time ", self), 0, 2)
        # row 1
        layout.addWidget(PySide.QtGui.QLabel("last buy", self), 1, 0)
        self.lPriceBuy = PySide.QtGui.QLineEdit("0.0", self)
        layout.addWidget(self.lPriceBuy, 1, 1)

        self.lPriceBuyTime = PySide.QtGui.QLineEdit("00:00:00", self)
        layout.addWidget(self.lPriceBuyTime, 1, 2)
        # row 3
        layout.addWidget(PySide.QtGui.QLabel("last sell", self), 2, 0)
        self.EditStateSell = PySide.QtGui.QLineEdit("0.0", self)
        layout.addWidget(self.EditStateSell, 2, 1)

        self.lPriceSellTime = PySide.QtGui.QLineEdit("00:00:00", self)
        layout.addWidget(self.lPriceSellTime, 2, 2)

        # header 2
        layout.addWidget(PySide.QtGui.QLabel("     ", self), 3, 0)
        layout.addWidget(PySide.QtGui.QLabel("buys ", self), 3, 1)
        layout.addWidget(PySide.QtGui.QLabel("sells", self), 3, 2)
        # row 4
        layout.addWidget(PySide.QtGui.QLabel("factor_buy_fix", self), 4, 0)
        self.qedit_factor_buy_fix = PySide.QtGui.QLineEdit(self)
        layout.addWidget(self.qedit_factor_buy_fix, 4, 1)
        self.qedit_factor_buy_fix.textChanged.connect(lambda value: GloVar.set("factor_buy_fix", float(value)))

        layout.addWidget(PySide.QtGui.QLabel("factor_sell_fix", self), 4, 0)
        self.qedit_factor_sell_fix = PySide.QtGui.QLineEdit(self)
        layout.addWidget(self.qedit_factor_sell_fix, 4, 2)
        self.qedit_factor_sell_fix.textChanged.connect(lambda value: GloVar.set("factor_sell_fix", float(value)))

        # row 5
        layout.addWidget(PySide.QtGui.QLabel("factor_buy_var", self), 5, 0)
        self.qedit_factor_buy_var = PySide.QtGui.QLineEdit(self)
        layout.addWidget(self.qedit_factor_buy_var, 5, 1)
        self.qedit_factor_buy_var.textChanged.connect(lambda value: GloVar.set("factor_buy_var", float(value)))

        layout.addWidget(PySide.QtGui.QLabel("factor_sell_var", self), 5, 0)
        self.qedit_factor_sell_var = PySide.QtGui.QLineEdit(self)
        layout.addWidget(self.qedit_factor_sell_var, 5, 2)
        self.qedit_factor_sell_var.textChanged.connect(lambda value: GloVar.set("factor_sell_var", float(value)))

        self.setLayout(layout)

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
