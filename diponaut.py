import PySide2.QtGui
from logic.TradeGlobals import GloVar
import gui.MainWindow
import sys
import re

GloVar.loadArguments(sys.argv)

app = PySide2.QtGui.QApplication([])
MainWidget = gui.MainWindow.Main(parent=None)
MainWidget.resize(800, 800)
MainWidget.show()
app.exec_()
