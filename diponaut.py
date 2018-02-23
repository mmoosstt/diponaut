import PySide.QtGui
from logic.TradeGlobals import GloVar
import gui.MainWindow
import sys
import re

args = sys.argv[1:]

if args != []:
    for arg in args:

        _res = re.findall("-(.*):(.*)", arg)

        if len(_res[0]) == 2:

            GloVarName = _res[0][0]
            GloVarValue = _res[0][1]

            if GloVarName in GloVar.__dict__.keys():
                GloVar.set(GloVarName, GloVarValue)
                print("GloVar.set(%s,%s)".format(GloVarName, GloVarValue))


app = PySide.QtGui.QApplication([])
MainWidget = gui.MainWindow.Main(parent=None,
                                 simulation=False,
                                 update_rate_trade_data=10.,
                                 update_rate_plotting=10.,
                                 update_rate_save_data=100)
MainWidget.resize(800, 800)
MainWidget.show()
app.exec_()
