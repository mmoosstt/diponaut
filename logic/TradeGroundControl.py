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

                    if (_m_dict['symbol'] == GloVar.get("trade_symbol") and
                            int(_m_dict['cycle_time']) == GloVar.get("trade_cycle_time")):

                        _year = int(_m_dict['year'])
                        _mon = int(_m_dict['mon'])
                        _day = int(_m_dict['day'])
                        _str = "{0:04d}{1:02d}{2:02d}".format(_year, _mon, _day)
                        _val = int(_str, 10)
                        _results[_val] = _m_dict

        _result_key = sorted(_results.keys())

        if _result_key != []:
            _result_key = _result_key[-1:][0]
            _return = _results[_result_key]

        else:
            _return_key = False
            _return = False

        return _return, _result_key


class FilePathes(object):

    def __init__(self):

        self.path_storage = ""
        self.path_temp = ""
        self.path_config = ""
        self.file_path_config = ""
        self.file_path_logger = ""
        self.file_path_prediction = ""
        self.file_path_states = ""
        self.file_path_sim = ""
        self.changed = False
        self.update()

    def update(self):

        self.changed = False
        # update pathes
        _path_storage = "{0}/{1}".format(GloVar.get("path_storage"), GloVar.get("trade_symbol"))
        _path_temp = "{0}/{1}".format(GloVar.get("path_temp"), GloVar.get("trade_symbol"))
        _path_config = GloVar.get("path_config")

        def _inline_update_pathes(old, new):
            if old != new:
                old = new
                self.changed = True

                if not os.path.isdir(old):
                    os.makedirs(old)

            return old

        self.path_config = _inline_update_pathes(self.path_config, _path_config)
        self.path_storage = _inline_update_pathes(self.path_storage, _path_storage)
        self.path_temp = _inline_update_pathes(self.path_temp, _path_temp)

        # update file_pathes
        _file_path_sim = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("sim"))
        _file_path_logger = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("logger"))
        _file_path_prediction = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("prediction"))
        _file_path_states = "{0}/{1}".format(self.path_temp, FileName.create_new_file_id("states"))

        def _inline_update_files(old, new, file_key):

            if old == new:
                _return = old

            else:
                _return = new

                self.changed = True

                # copy latest from storge if new file does not exists
                if not os.path.isfile(new):

                    _file_match1, _time_stamp1 = FileName.find_latest_file_id(self.path_storage)
                    _file_match2, _time_stamp2 = FileName.find_latest_file_id(self.path_temp)

                    if isinstance(_file_match1, dict) and _file_match2 == False:
                        _match = _file_match1
                        _path = self.path_storage

                    elif isinstance(_file_match2, dict) and _file_match1 == False:
                        _match = _file_match2
                        _path = self.path_temp

                    elif _file_match2 == False and _file_match1 == False:
                        _match = False
                        _path = False

                    elif _time_stamp2 > _time_stamp1:
                        _match = _file_match2
                        _path = self.path_temp
                        print('copy from temp path')

                    else:
                        _match = _file_match1
                        _path = self.path_storage
                        print("copy from storage path")

                    if _match != False:
                        _match["file_key"] = file_key
                        _storage_path = "{0}/{1}".format(_path, FileName.create_file_id(_match))

                        if os.path.isfile(_storage_path):
                            try:
                                shutil.copy(_storage_path, new)
                            except shutil.SameFileError:
                                pass

            return _return

        self.file_path_sim = _inline_update_files(self.file_path_sim, _file_path_sim, "sim")
        self.file_path_logger = _inline_update_files(self.file_path_logger, _file_path_logger, "logger")
        self.file_path_prediction = _inline_update_files(self.file_path_prediction, _file_path_prediction, "prediction")
        self.file_path_states = _inline_update_files(self.file_path_states, _file_path_states, "states")
        self.file_path_config = "{0}/{1}".format(self.path_config, "config.xml")

        return self.changed


class GroundControl(object):

    def __init__(self, simulation=True):
        self.simulation = simulation
        self.files = FilePathes()
        self.changed = False

    def load_config(self):

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

        self.changed = self.files.update()
        if self.changed:
            self.load_config()

        self.logger.update()
        self.prediction.update(self.logger)
        self.state.update(self.prediction.prediction)

        return self.changed

    def save(self):

        if self.simulation == False and self.changed == False:
            self.logger.save_storage()
            self.prediction.save_storage()
            self.state.save_storage()


if __name__ == "__main__":
    import sys
    os.chdir(os.path.abspath("../"))
    _i = FilePathes()
