import PySide
import PySide.QtGui
import PySide.QtCore
import DataApi


class TraidingView(PySide.QtGui.QWidget):

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
        self.lPriceSell = PySide.QtGui.QLineEdit("0.0", self)
        layout.addWidget(self.lPriceSell, 2, 1)
        self.lPriceSellTime = PySide.QtGui.QLineEdit("00:00:00", self)
        layout.addWidget(self.lPriceSellTime, 2, 2)

        # header 2
        layout.addWidget(PySide.QtGui.QLabel("     ", self), 3, 0)
        layout.addWidget(PySide.QtGui.QLabel("buys ", self), 3, 1)
        layout.addWidget(PySide.QtGui.QLabel("sells", self), 3, 2)
        # row 4
        layout.addWidget(PySide.QtGui.QLabel("limit factor fix", self), 4, 0)
        self.iFactorFixBuy = PySide.QtGui.QLineEdit(self)
        layout.addWidget(self.iFactorFixBuy, 4, 1)
        self.iFactorFixSell = PySide.QtGui.QLineEdit(self)
        layout.addWidget(self.iFactorFixSell, 4, 2)
        # row 5
        layout.addWidget(PySide.QtGui.QLabel("limit factor var", self), 5, 0)
        self.iFactorFixBuy = PySide.QtGui.QLineEdit(self)
        layout.addWidget(self.iFactorFixBuy, 5, 1)
        self.iFactorFixSell = PySide.QtGui.QLineEdit(self)
        layout.addWidget(self.iFactorFixSell, 5, 2)

        self.setLayout(layout)

    def SetDataStates(self, Data):

        if isinstance(Data, DataApi.TradingStates):
            self.data_state = Data

    def SetDataPrediction(self, Data):

        if isinstance(Data, DataApi.TradingPrediction):
            self.dataPrediction = Data


if __name__ == "__main__":
    app = PySide.QtGui.QApplication([])

    MainWidget = TraidingData()
    MainWidget.resize(800, 800)
    MainWidget.show()
    app.exec_()
