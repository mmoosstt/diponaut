import PySide.QtGui
import gui.LivePlotter
import gui.GlobalVariables


class Main(PySide.QtGui.QWidget):

    def __init__(self,
                 parent=None,
                 symbol='TRXETH',
                 time_delta=10,
                 file_path_data="./data_sim",
                 file_path_config="./data/config.xml",
                 simulation=False,
                 update_rate=0.1):

        PySide.QtGui.QWidget.__init__(self, parent)

        self.layout = PySide.QtGui.QHBoxLayout(self)

        self.layout.addWidget(gui.GlobalVariables.GlobalVariables(self), 1)

        _w = gui.LivePlotter.TraidingWidget(self, symbol, time_delta, file_path_data, file_path_config, simulation, update_rate=0.1)
        self.layout.addWidget(_w, 4)

        self.setLayout(self.layout)
