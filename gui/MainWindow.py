import PySide.QtGui
import gui.LivePlotter
import gui.GlobalVariables


class Main(PySide.QtGui.QWidget):

    def __init__(self, parent=None):
        PySide.QtGui.QWidget.__init__(self, parent)

        self.layout = PySide.QtGui.QHBoxLayout(self)
        self.layout.addWidget(gui.GlobalVariables.GlobalVariables(self), 1)
        self.layout.addWidget(gui.LivePlotter.TraidingWidget(self), 4)

        self.setLayout(self.layout)
