import PySide.QtGui
import pyqtgraph
import faulthandler
faulthandler.enable()
import logic.DataApi
import scipy
import numpy as np


class TraidingWidget(PySide.QtGui.QWidget):

    color_cnt = 1

    def __init__(self, parent=None):
        PySide.QtGui.QWidget.__init__(self, parent)
        self.data = logic.DataApi.TradesLogger(time_delta=10, symbol="TRXETH")
        self.data_prediction = logic.DataApi.TradesPrediction(time_delta=10)

        self.layout = PySide.QtGui.QVBoxLayout(self)

        self.createPlotInterface()
        self.setLayout(self.layout)
        self.qtimer = PySide.QtCore.QTimer()
        self.qtimer.timeout.connect(self.updateTrades)
        self.qtimer.start(1000)
        self.qtimer.setSingleShot(True)

        self.qtimer_update_xachses = PySide.QtCore.QTimer()
        self.qtimer_update_xachses.setSingleShot(True)
        self.qtimer_update_xachses.timeout.connect(self.timeout_sync_x_aches)

    def updateTrades(self):
        self.data.update_ring()
        self.data_prediction.update(self.data)
        self.drawPlots()
        self.qtimer.start(10000)

    def createPlotInterface(self):

        def mySetSymbol(w):
            w.setSymbol(1)

        self.plotWidgets = {}
        self.plotWidgets["plot1"] = {}
        self.plotWidgets["plot1"]["widget"] = pyqtgraph.PlotWidget(self)
        self.plotWidgets["plot1"]["curves"] = {}
        self.plotWidgets["plot1"]["curves"]["value_mean"] = {}
        self.plotWidgets["plot1"]["curves"]["value_mean"]["widget"] = self.plotWidgets["plot1"]["widget"].plot()
        self.plotWidgets["plot1"]["curves"]["value_mean"]["x"] = self.data.ring_trades_time
        self.plotWidgets["plot1"]["curves"]["value_mean"]["y"] = self.data.ring_value_mean_quantity

        self.plotWidgets["plot1"]["curves"]["value_flit1"] = {}
        self.plotWidgets["plot1"]["curves"]["value_flit1"]["widget"] = self.plotWidgets["plot1"]["widget"].plot()
        self.plotWidgets["plot1"]["curves"]["value_flit1"]["x"] = self.data_prediction.trades_time
        self.plotWidgets["plot1"]["curves"]["value_flit1"]["y"] = self.data_prediction.trades_filt1

        self.plotWidgets["plot1"]["curves"]["value_filt2"] = {}
        self.plotWidgets["plot1"]["curves"]["value_filt2"]["widget"] = self.plotWidgets["plot1"]["widget"].plot()
        self.plotWidgets["plot1"]["curves"]["value_filt2"]["x"] = self.data_prediction.trades_time
        self.plotWidgets["plot1"]["curves"]["value_filt2"]["y"] = self.data_prediction.trades_filt2

        self.plotWidgets["plot2"] = {}
        self.plotWidgets["plot2"]["widget"] = pyqtgraph.PlotWidget(self)
        self.plotWidgets["plot2"]["curves"] = {}
        self.plotWidgets["plot2"]["curves"]["filt1-filt2"] = {}
        self.plotWidgets["plot2"]["curves"]["filt1-filt2"]["widget"] = self.plotWidgets["plot2"]["widget"].plot()
        self.plotWidgets["plot2"]["curves"]["filt1-filt2"]["x"] = self.data_prediction.trades_time
        self.plotWidgets["plot2"]["curves"]["filt1-filt2"]["y"] = self.data_prediction.trades_err

        self.plotWidgets["plot2"]["curves"]["trades_ana1"] = {}
        self.plotWidgets["plot2"]["curves"]["trades_ana1"]["widget"] = self.plotWidgets["plot2"]["widget"].plot()
        self.plotWidgets["plot2"]["curves"]["trades_ana1"]["x"] = self.data_prediction.trades_time
        self.plotWidgets["plot2"]["curves"]["trades_ana1"]["y"] = self.data_prediction.trades_err_ana
        self.plotWidgets["plot2"]["curves"]["trades_ana1"]["style"] = lambda w: mySetSymbol(w)

        self.plotWidgets["plot2"]["curves"]["trades_buy"] = {}
        self.plotWidgets["plot2"]["curves"]["trades_buy"]["widget"] = self.plotWidgets["plot2"]["widget"].plot()
        self.plotWidgets["plot2"]["curves"]["trades_buy"]["x"] = self.data_prediction.trades_time
        self.plotWidgets["plot2"]["curves"]["trades_buy"]["y"] = self.data_prediction.trades_buy

        self.plotWidgets["plot2"]["curves"]["trades_sell"] = {}
        self.plotWidgets["plot2"]["curves"]["trades_sell"]["widget"] = self.plotWidgets["plot2"]["widget"].plot()
        self.plotWidgets["plot2"]["curves"]["trades_sell"]["x"] = self.data_prediction.trades_time
        self.plotWidgets["plot2"]["curves"]["trades_sell"]["y"] = self.data_prediction.trades_sell

        self.plotWidgets["plot3"] = {}
        self.plotWidgets["plot3"]["widget"] = pyqtgraph.PlotWidget(self)
        self.plotWidgets["plot3"]["curves"] = {}
        self.plotWidgets["plot3"]["curves"]["ring_trades_count"] = {}
        self.plotWidgets["plot3"]["curves"]["ring_trades_count"]["widget"] = self.plotWidgets["plot3"]["widget"].plot()
        self.plotWidgets["plot3"]["curves"]["ring_trades_count"]["x"] = self.data.ring_trades_time
        self.plotWidgets["plot3"]["curves"]["ring_trades_count"]["y"] = self.data.ring_trades_count

        for _plot_key in sorted(self.plotWidgets.keys()):
            self.layout.addWidget(self.plotWidgets[_plot_key]["widget"])
            self.plotWidgets[_plot_key]["widget"].sigRangeChanged.connect(self.event_sync_x_aches)
            _legend = self.plotWidgets[_plot_key]["widget"].addLegend()

            for _curve_key in sorted(self.plotWidgets[_plot_key]["curves"]):
                _legend.addItem(self.plotWidgets[_plot_key]["curves"][_curve_key]["widget"], name=_curve_key)

    def event_sync_x_aches(self, widget, cords):
        self._store_cords = cords
        self.qtimer_update_xachses.start(100)

    def timeout_sync_x_aches(self):
        for _plot_key in sorted(self.plotWidgets.keys()):
            _widget = self.plotWidgets[_plot_key]["widget"]
            _widget.sigRangeChanged.disconnect(self.event_sync_x_aches)

        for _plot_key in sorted(self.plotWidgets.keys()):
            _widget = self.plotWidgets[_plot_key]["widget"]
            _widget.setXRange(self._store_cords[0][0], self._store_cords[0][1])

        for _plot_key in sorted(self.plotWidgets.keys()):
            _widget = self.plotWidgets[_plot_key]["widget"]
            _widget.sigRangeChanged.connect(self.event_sync_x_aches)

    def drawPlots(self):

        for _plot_key in sorted(self.plotWidgets.keys()):
            _plotWidget = self.plotWidgets[_plot_key]['widget']

            _xMin = -1e10
            _xMax = 1e10
            _yMin = -1e10
            _yMax = 1e10

            for _curve_key in sorted(self.plotWidgets[_plot_key]["curves"].keys()):
                _curveWidget = self.plotWidgets[_plot_key]['curves'][_curve_key]["widget"]
                _x = self.plotWidgets[_plot_key]['curves'][_curve_key]["x"]
                _y = self.plotWidgets[_plot_key]['curves'][_curve_key]["y"]

                #_xMin = max(_xMin, min(_x))
                #_xMax = min(_xMax, max(_x))

                #_yMin = max(_yMin, min(_y))
                #_yMax = min(_yMax, max(_y))

                _curveWidget.setData(x=_x, y=_y)
                _curveWidget.setPen(pyqtgraph.mkPen(width=1.5, color=self.color_cnt))

                if "style" in self.plotWidgets[_plot_key]['curves'][_curve_key].keys():
                    _style = self.plotWidgets[_plot_key]['curves'][_curve_key]["style"]
                    _style(_curveWidget)
                    _curveWidget.setPen(None)

                self.color_cnt += 0xF

            #_plotWidget.setXRange(min(_x), max(_x))
            #_plotWidget.setYRange(min(_not_null), max(_not_null))

            self.color_cnt = 1

# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':

    app = PySide.QtGui.QApplication([])
    MainWidget = TraidingWidget()
    MainWidget.resize(800, 800)
    MainWidget.show()
    app.exec_()
