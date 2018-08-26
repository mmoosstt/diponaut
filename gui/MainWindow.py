import PySide2.QtWidgets
from gui import LivePlotter, GlobalVariables, TradingInterface
from logic.TradeGlobals import GloVar
from gui.TradingInterface import TraidingInterface


class Main(PySide2.QtWidgets.QWidget):

    def __init__(self, parent=None):

        PySide2.QtWidgets.QWidget.__init__(self, parent)

        hbox = PySide2.QtWidgets.QHBoxLayout()
        vbox =  PySide2.QtWidgets.QVBoxLayout()

        self.traiding_interface = TradingInterface.TraidingInterface(self)
        vbox.addWidget(self.traiding_interface)
        vbox.addWidget(GlobalVariables.GlobalVariables(self))

        hbox.addLayout(vbox,1)
        
        self.plotter_interface = LivePlotter.TraidingWidget(self)
        hbox.addWidget(self.plotter_interface,4)

        self.traiding_interface.button_data_reset.clicked.connect(self.plotter_interface.GroundControl.logger.reset)
        
        self.setLayout(hbox)

        GloVar.emit_all()