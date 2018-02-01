import PySide.QtGui
import gui.MainWindow

app = PySide.QtGui.QApplication([])
MainWidget = gui.MainWindow.Main()
MainWidget.resize(800, 800)
MainWidget.show()
app.exec_()