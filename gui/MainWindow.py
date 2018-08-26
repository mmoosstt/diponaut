import PySide2.QtWidgets
from gui import LivePlotter, GlobalVariables, TradingInterface
from logic.TradeGlobals import GloVar


class Main(PySide2.QtWidgets.QWidget):

    def __init__(self, parent=None):

        PySide2.QtWidgets.QWidget.__init__(self, parent)

        hbox = PySide2.QtWidgets.QHBoxLayout()
        vbox =  PySide2.QtWidgets.QVBoxLayout()


        vbox.addWidget(TradingInterface.TraidingInterface(self))
        vbox.addWidget(GlobalVariables.GlobalVariables(self))

        hbox.addLayout(vbox,1)
        
        hbox.addWidget(LivePlotter.TraidingWidget(self),4)

        self.setLayout(hbox)

        GloVar.emit_all()