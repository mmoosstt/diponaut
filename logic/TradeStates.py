import time
import h5py
import os
import numpy
import threading
from logic.TradeLogger import TradeInterfaceNotInitialised
from logic.TradeGlobals import GloVar


class TradeInterfaceNotInitialised(Exception):
    pass


class States(object):

    def __init__(self, file_path):
        self.ring_data_filepath = file_path
        self.state = GloVar.get("state")
        self.state_z = GloVar.get("state")
        self.zc_cnt = 0
        self.ring_size = int(60 * 60 * 24 / GloVar.get("trade_cycle_time"))
        self.events_buy = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.events_sell = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.events_zc = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.events_buy_time = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.events_sell_time = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.events_zc_time = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)

        if not os.path.isfile(self.ring_data_filepath):
            self.save_storage()

        self.load_storage()

    def init_trade_interface(self, trade_interface):
        self.trade_interface = trade_interface

    def load_storage(self):
        _f = h5py.File(self.ring_data_filepath, 'r')
        self.events_buy = numpy.array(_f['events_buy'], dtype=numpy.double)
        self.events_buy_time = numpy.array(_f['events_buy_time'], dtype=numpy.double)
        self.events_sell = numpy.array(_f['events_sell'], dtype=numpy.double)

        self.events_sell_time = numpy.array(_f['events_sell_time'], dtype=numpy.double)
        self.events_zc = numpy.array(_f['events_zc'], dtype=numpy.double)
        self.events_zc_time = numpy.array(_f['events_zc_time'], dtype=numpy.double)
        _f.close()

    def save_storage(self, file_path=None):

        if file_path != None:
            self.ring_data_filepath = file_path

        _f = h5py.File(self.ring_data_filepath, 'w')
        _f.create_dataset('events_buy', data=self.events_buy)
        _f.create_dataset('events_buy_time', data=self.events_buy_time)
        _f.create_dataset('events_sell', data=self.events_sell)
        _f.create_dataset('events_sell_time', data=self.events_sell_time)
        _f.create_dataset('events_zc', data=self.events_zc)
        _f.create_dataset('events_zc_time', data=self.events_zc_time)
        _f.close()

    def update(self, prediction_data):

        if self.trade_interface == None:
            raise TradeInterfaceNotInitialised

        def _add_event(events_arr, event, value):

            if event:
                numpy.copyto(events_arr[:-1], events_arr[1:])
                events_arr[len(events_arr) - 1] = value

        if (GloVar.get("state") == "START"):
            GloVar.set("state", "start")
            self.state = "start"

        if (GloVar.get("state") == "STOP"):
            GloVar.set("state", "STOPPED")
            self.state = "STOPPED"
            self.state_z = "STOPPED"

        if self.state == "week_buy":
            self.week_buy_cnt += 1
        else:
            self.week_buy_cnt = 0

        if self.state == "week_sell" and prediction_data.event_sell == False:
            self.week_sell_cnt += 1
        else:
            self.week_sell_cnt = 0

        if prediction_data.event_zc:
            self.zc_cnt = min(3, self.zc_cnt + 1)

        else:
            self.zc_cnt = max(0, self.zc_cnt - 1)

        prediction_data.event_zc = False
        if self.zc_cnt >= 3:
            prediction_data.event_zc = True

            _add_event(self.events_zc_time, True, prediction_data.event_time)
            _add_event(self.events_zc, True, prediction_data.event_price)

            GloVar.set("state_zero_crossing_price", prediction_data.event_price)
            GloVar.set("state_zero_crossing_time", prediction_data.event_time)

            print("zero crossing")

        if (
            (self.state == "start" or
             self.state == "stro_sell") and
                prediction_data.event_buy == True):

            self.state = "week_buy"
            self.price_week = prediction_data.event_price
            GloVar.set("filt1_hz", 0.025)

        elif (self.state == "week_buy" and
              (prediction_data.event_zc == True and prediction_data.event_buy == True)):
            self.state = "stro_buy"

            self.trade_interface.create_buy_order()

            _add_event(self.events_buy_time, True, prediction_data.event_time)
            _add_event(self.events_buy, True, prediction_data.event_price)
            GloVar.set("state_buy_price", prediction_data.event_price)
            GloVar.set("state_buy_time", prediction_data.event_time)
            GloVar.set("state_sell_lost_limit", prediction_data.event_price * 0.925)
            GloVar.set("state_sell_win_limit", prediction_data.event_price * 1.025)
            GloVar.set("filt1_hz", 0.01)

        elif (self.state == "stro_buy" and prediction_data.event_price < GloVar.get("state_sell_lost_limit")):
            self.state = "sell_now_stop_lost"

        elif (self.state == "stro_buy" and prediction_data.event_price > GloVar.get("state_sell_win_limit") and GloVar.get("filt1_grad") < 0):
            self.state = "sell_now_take_win"

        elif (self.state == "stro_buy" and
              prediction_data.event_sell == True):
            self.state = "week_sell"
            self.price_week = prediction_data.event_price
            GloVar.set("filt1_hz", 0.025)

        elif (self.state == "week_sell" and
              (prediction_data.event_zc == True or
               (prediction_data.event_sell == False and self.week_sell_cnt >= 6))
              ):

            self.state = "sell_now_zero_crossing"

        if (self.state != self.state_z):
            GloVar.set("state", self.state)
            self.state_z = self.state

            print(self.state, time.ctime(time.time()), prediction_data.event_price)

        if (self.state.startswith("sell_now")):
            self.state = "stro_sell"

            self.trade_interface.create_sell_order()
            _add_event(self.events_sell_time, True, prediction_data.event_time)
            _add_event(self.events_sell, True, prediction_data.event_price)

            GloVar.set("state_sell_price", prediction_data.event_price)
            GloVar.set("state_sell_time", prediction_data.event_time)
            GloVar.set("order_delta_price", self.events_sell[-1:][0] - self.events_buy[-1:][0])
            GloVar.set("filt1_hz", 0.01)

        if (self.state != self.state_z):
            GloVar.set("state", self.state)
            self.state_z = self.state

            print(self.state, time.ctime(time.time()), prediction_data.event_price)
