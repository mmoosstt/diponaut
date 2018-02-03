import PySide.QtGui
import gui.MainWindow

app = PySide.QtGui.QApplication([])
MainWidget = gui.MainWindow.Main(parent=None,
                                 simulation=True,
                                 update_rate_trade_data=0.001,
                                 update_rate_plotting=10.,
                                 update_rate_save_data=100)

MainWidget.resize(800, 800)
MainWidget.show()
app.exec_()