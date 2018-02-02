import PySide.QtGui
import gui.MainWindow

app = PySide.QtGui.QApplication([])
MainWidget = gui.MainWindow.Main(parent=None,
                                 symbol='TRXETH',
                                 time_delta=10,
                                 file_path_data="./data_sim",
                                 file_path_config="./data/config.xml",
                                 simulation=True,
                                 update_rate=0.001)

MainWidget.resize(800, 800)
MainWidget.show()
app.exec_()