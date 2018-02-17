import logic.TradeApi
import logic.TradeApiSim
import logic.TradeLogger
import logic.TradePrediction
import logic.TradeStates
from logic.TradeGlobals import GloVar
import time
import re
import os
import shutil


class FileName(object):

    @staticmethod
    def create_new_file_id(key):
        _t = time.gmtime()
        return "{3}_{0:02d}_{1:02d}_{2:02d}_{4}s-{5}.hdf".format(_t.tm_year,
                                                                 _t.tm_mon,
                                                                 _t.tm_mday,
                                                                 GloVar.get("trade_symbol"),
                                                                 GloVar.get("trade_cycle_time"),
                                                                 key)

    @staticmethod
    def create_file_id(match_dict):
        _t = time.gmtime()
        return "{3}_{0:02d}_{1:02d}_{2:02d}_{4}s-{5}.hdf".format(int(match_dict['year']),
                                                                 int(match_dict['mon']),
                                                                 int(match_dict['day']),
                                                                 match_dict['symbol'],
                                                                 int(match_dict['cycle_time']),
                                                                 match_dict['file_key'])

    @staticmethod
    def find_file_id(input):
        _c = re.compile("(?P<symbol>[A-Z]*)_(?P<year>[0-9]{2,4})_(?P<mon>[0-9]{2,4})_(?P<day>[0-9]{2,4})_(?P<cycle_time>[0-9]{1,3})s-(?P<file_key>[a-z]*)\.?")
        _r = _c.search(input)
        return _r

    @staticmethod
    def find_latest_file_id(path):

        _results = {}
        for _path, _folder, _files in os.walk(path):
            for _file in _files:
                _m = FileName.find_file_id(_file)
                _m_dict = _m.groupdict()

                if _m_dict:
                    if _m_dict['symbol'] == GloVar.get("trade_symbol"):
                        _year = int(_m_dict['year'])
                        _mon = int(_m_dict['mon'])
                        _day = int(_m_dict['day'])
                        _str = "{0:04d}{1:02d}{2:02d}".format(_year, _mon, _day)
                        _val = int(_str, 10)
                        _results[_val] = _m_dict

        _result_key = sorted(_results.keys())[-1:][0]
        return _results[_result_key]


class FilePathes(object):

    def __init__(self):

        self.path_storage = GloVar.get("path_storage")
        self.path_temp = GloVar.get("path_temp")
        self.path_config = GloVar.get("path_config")

        if not os.path.isdir(self._path_temp):
            os.makedirs(self._path_temp)

        self.file_path_config = "{0}/{1}".format(self.path_config, "config.xml")
        self.file_path_sim = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("sim"))
        self.file_path_logger = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("logger"))
        self.file_path_prediction = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("prediction"))
        self.file_path_states = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("states"))

        match_dict = FileName.find_latest_file_id(self.path_storage)

        def shutil_copy(source, destination):
            try:
                shutil.copy(source, destination)
            except shutil.SameFileError:
                pass

        # sim
        match_dict['file_key'] = "sim"
        _source_path = "{0}/{1}".format(self.path_storage, FileName.create_file_id(match_dict))
        shutil_copy(_source_path, self.file_path_sim,)

        # logger
        match_dict['file_key'] = "logger"
        _source_path = "{0}/{1}".format(self.path_storage, FileName.create_file_id(match_dict))
        shutil_copy(_source_path, self.file_path_logger)

        # prediction
        match_dict['file_key'] = "prediction"
        _source_path = "{0}/{1}".format(self.path_storage, FileName.create_file_id(match_dict))
        shutil_copy(_source_path, self.file_path_prediction)

        # states
        match_dict['file_key'] = "states"
        _source_path = "{0}/{1}".format(self.path_storage, FileName.create_file_id(match_dict))
        shutil_copy(_source_path, self.file_path_states)

    def update_temp_pathes(self):
        self.file_path_sim = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("sim"))
        self.file_path_logger = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("logger"))
        self.file_path_prediction = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("prediction"))
        self.file_path_states = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("states"))


class GroundControl(object):

    def __init__(self, simulation=True):
        self.simulation = simulation
        self.files = FilePathes()

    def load_config(self):

        self.symbol = GloVar.get("trade_symbol")
        self.trade_cycle_time = GloVar.get("trade_cycle_time")

        if self.simulation:
            self.api = logic.TradeApiSim.Api(self.files.file_path_sim)
        else:
            self.api = logic.TradeApi.Api(self.files.file_path_config)

        self.logger = logic.TradeLogger.Logger(self.files.file_path_logger)
        self.prediction = logic.TradePrediction.Prediction(self.files.file_path_prediction)
        self.state = logic.TradeStates.States(self.files.file_path_states)

        self.logger.init_trade_interface(self.api)
        self.state.init_trade_interface(self.api)

    def update(self):
        self.logger.update()
        self.prediction.update(self.logger)
        self.state.update(self.prediction.prediction)

    def save(self):
        if self.simulation == False:
            self.files.update_temp_pathes()
            self.logger.save_storage(self.files.file_path_logger)
            self.prediction.save_storage(self.files.file_path_prediction)
            self.state.save_storage(self.files.file_path_states)


if __name__ == "__main__":
    _i = FilePathes()
