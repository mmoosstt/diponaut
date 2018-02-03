import PySide.QtGui
import pyqtgraph
import faulthandler
faulthandler.enable()
import time
from logic.TradeGroundControl import GroundControl


class TimeAxisItem(pyqtgraph.AxisItem):

    def __init__(self, *args, **kwargs):
        pyqtgraph.AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):

        _t_str = []
        for _v in values:
            _t = time.gmtime(_v)
            _s = "{0:02}:{1:02}:{2:02}".format(_t.tm_hour, _t.tm_min, _t.tm_sec)
            _t_str.append(_s)

        return _t_str


class TraidingWidget(PySide.QtGui.QWidget):

    color_cnt = 1

    def __init__(self, parent=None, simulation=True, update_rate_trade_data=10, update_rate_plotting=10, update_rate_save_data=100):
        PySide.QtGui.QWidget.__init__(self, parent)
        self.simulation = True
        self.GroundControl = GroundControl(self.simulation)
        self.GroundControl.load_config()

        self.layout = PySide.QtGui.QVBoxLayout(self)

        self.createPlotInterface()
        self.setLayout(self.layout)
        self.qtimer = PySide.QtCore.QTimer()
        self.qtimer.timeout.connect(self.updateTradeData)
        self.qtimer.start(1000 * update_rate_trade_data)

        self.save_counter = min(10, abs(int(update_rate_save_data / update_rate_trade_data)))
        self.save_counter_z = 0

        self.qtimer2 = PySide.QtCore.QTimer()
        self.qtimer2.timeout.connect(self.updateTradePlots)
        self.qtimer2.start(1000 * update_rate_plotting)

        self.qtimer3 = PySide.QtCore.QTimer()
        self.qtimer3.setSingleShot(True)
        self.qtimer3.timeout.connect(self.timeout_sync_x_aches)

    def updateTradeData(self):
        self.GroundControl.update()

        if self.save_counter_z > self.save_counter:
            self.save_counter_z = 0
            self.GroundControl.save()
        else:
            self.save_counter_z += 1

    def createPlotInterface(self):

        def mySetSymbol(w, s):
            w.setSymbol(s)
            w.setPen(None)

        self.plotWidgets = {}
        self.plotWidgets["plot1"] = {}
        self.plotWidgets["plot1"]["widget"] = pyqtgraph.PlotWidget(self, axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plotWidgets["plot1"]["curves"] = {}
        self.plotWidgets["plot1"]["curves"]["value_mean"] = {}
        self.plotWidgets["plot1"]["curves"]["value_mean"]["widget"] = self.plotWidgets["plot1"]["widget"].plot()
        self.plotWidgets["plot1"]["curves"]["value_mean"]["x"] = self.GroundControl.logger.ring_trades_time
        self.plotWidgets["plot1"]["curves"]["value_mean"]["y"] = self.GroundControl.logger.ring_value_mean_quantity

        self.plotWidgets["plot1"]["curves"]["value_flit1"] = {}
        self.plotWidgets["plot1"]["curves"]["value_flit1"]["widget"] = self.plotWidgets["plot1"]["widget"].plot()
        self.plotWidgets["plot1"]["curves"]["value_flit1"]["x"] = self.GroundControl.prediction.trades_time
        self.plotWidgets["plot1"]["curves"]["value_flit1"]["y"] = self.GroundControl.prediction.trades_filt1

        self.plotWidgets["plot1"]["curves"]["value_filt2"] = {}
        self.plotWidgets["plot1"]["curves"]["value_filt2"]["widget"] = self.plotWidgets["plot1"]["widget"].plot()
        self.plotWidgets["plot1"]["curves"]["value_filt2"]["x"] = self.GroundControl.prediction.trades_time
        self.plotWidgets["plot1"]["curves"]["value_filt2"]["y"] = self.GroundControl.prediction.trades_filt2

        self.plotWidgets["plot1"]["curves"]["events_buy"] = {}
        self.plotWidgets["plot1"]["curves"]["events_buy"]["widget"] = self.plotWidgets["plot1"]["widget"].plot(symbolSize=10, symbol=1)
        self.plotWidgets["plot1"]["curves"]["events_buy"]["x"] = self.GroundControl.state.events_buy_time
        self.plotWidgets["plot1"]["curves"]["events_buy"]["y"] = self.GroundControl.state.events_buy
        self.plotWidgets["plot1"]["curves"]["events_buy"]["style"] = lambda w: mySetSymbol(w, 2)

        self.plotWidgets["plot1"]["curves"]["events_sell"] = {}
        self.plotWidgets["plot1"]["curves"]["events_sell"]["widget"] = self.plotWidgets["plot1"]["widget"].plot(symbolSize=10)
        self.plotWidgets["plot1"]["curves"]["events_sell"]["x"] = self.GroundControl.state.events_sell_time
        self.plotWidgets["plot1"]["curves"]["events_sell"]["y"] = self.GroundControl.state.events_sell
        self.plotWidgets["plot1"]["curves"]["events_sell"]["style"] = lambda w: mySetSymbol(w, 3)

        self.plotWidgets["plot1"]["curves"]["events_zero_crossing"] = {}
        self.plotWidgets["plot1"]["curves"]["events_zero_crossing"]["widget"] = self.plotWidgets["plot1"]["widget"].plot(symbolSize=7)
        self.plotWidgets["plot1"]["curves"]["events_zero_crossing"]["x"] = self.GroundControl.state.events_zc_time
        self.plotWidgets["plot1"]["curves"]["events_zero_crossing"]["y"] = self.GroundControl.state.events_zc
        self.plotWidgets["plot1"]["curves"]["events_zero_crossing"]["style"] = lambda w: mySetSymbol(w, 4)

        self.plotWidgets["plot2"] = {}
        self.plotWidgets["plot2"]["widget"] = pyqtgraph.PlotWidget(self, axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plotWidgets["plot2"]["curves"] = {}
        self.plotWidgets["plot2"]["curves"]["filt1-filt2"] = {}
        self.plotWidgets["plot2"]["curves"]["filt1-filt2"]["widget"] = self.plotWidgets["plot2"]["widget"].plot()
        self.plotWidgets["plot2"]["curves"]["filt1-filt2"]["x"] = self.GroundControl.prediction.trades_time
        self.plotWidgets["plot2"]["curves"]["filt1-filt2"]["y"] = self.GroundControl.prediction.trades_err

        self.plotWidgets["plot2"]["curves"]["trades_buy"] = {}
        self.plotWidgets["plot2"]["curves"]["trades_buy"]["widget"] = self.plotWidgets["plot2"]["widget"].plot()
        self.plotWidgets["plot2"]["curves"]["trades_buy"]["x"] = self.GroundControl.prediction.trades_time
        self.plotWidgets["plot2"]["curves"]["trades_buy"]["y"] = self.GroundControl.prediction.trades_buy

        self.plotWidgets["plot2"]["curves"]["trades_sell"] = {}
        self.plotWidgets["plot2"]["curves"]["trades_sell"]["widget"] = self.plotWidgets["plot2"]["widget"].plot()
        self.plotWidgets["plot2"]["curves"]["trades_sell"]["x"] = self.GroundControl.prediction.trades_time
        self.plotWidgets["plot2"]["curves"]["trades_sell"]["y"] = self.GroundControl.prediction.trades_sell

        self.plotWidgets["plot3"] = {}
        self.plotWidgets["plot3"]["widget"] = pyqtgraph.PlotWidget(self, axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plotWidgets["plot3"]["curves"] = {}
        self.plotWidgets["plot3"]["curves"]["ring_trades_count"] = {}
        self.plotWidgets["plot3"]["curves"]["ring_trades_count"]["widget"] = self.plotWidgets["plot3"]["widget"].plot()
        self.plotWidgets["plot3"]["curves"]["ring_trades_count"]["x"] = self.GroundControl.logger.ring_trades_time
        self.plotWidgets["plot3"]["curves"]["ring_trades_count"]["y"] = self.GroundControl.logger.ring_trades_count

        for _plot_key in sorted(self.plotWidgets.keys()):
            self.layout.addWidget(self.plotWidgets[_plot_key]["widget"])
            self.plotWidgets[_plot_key]["widget"].sigRangeChanged.connect(self.event_sync_x_aches)
            _legend = self.plotWidgets[_plot_key]["widget"].addLegend()

            for _curve_key in sorted(self.plotWidgets[_plot_key]["curves"]):
                _legend.addItem(self.plotWidgets[_plot_key]["curves"][_curve_key]["widget"], name=_curve_key)

    def event_sync_x_aches(self, widget, cords):
        self._store_cords = cords
        self.qtimer3.start(100)

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

    def updateTradePlots(self):

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
