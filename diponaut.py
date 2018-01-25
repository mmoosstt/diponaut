import gui.LivePlotter as diponaut

app = diponaut.PySide.QtGui.QApplication([])
MainWidget = diponaut.TraidingWidget()
MainWidget.resize(800, 800)
MainWidget.show()
app.exec_()