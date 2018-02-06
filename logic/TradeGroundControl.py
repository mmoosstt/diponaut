import logic.TradeApi
import logic.TradeApiSim
import logic.TradeLogger
import logic.TradePrediction
import logic.TradeStates
from logic.TradeGlobals import GloVar


class GroundControl(object):

    def __init__(self, simulation=True):
        self.simulation = simulation

    def load_config(self):

        self.symbol = GloVar.get("trade_symbol")
        self.trade_cycle_time = GloVar.get("trade_cycle_time")

        if self.simulation:
            self.api = logic.TradeApiSim.Api("./data_sim/{0}-{1}s-sim.hdf".format(self.symbol, self.trade_cycle_time))
            self.logger = logic.TradeLogger.Logger("./data_sim/{0}-{1}s-logger.hdf".format(self.symbol, self.trade_cycle_time))
            self.prediction = logic.TradePrediction.Prediction("./data_sim/{0}-{1}s-prediction.hdf".format(self.symbol, self.trade_cycle_time))
            self.state = logic.TradeStates.States("./data_sim/{0}-{1}s-states.hdf".format(self.symbol, self.trade_cycle_time))

        else:
            self.api = logic.TradeApiSim.Api("./data/{0}-{1}s-sim.hdf".format(self.symbol, self.trade_cycle_time))
            self.logger = logic.TradeLogger.Logger("./data/{0}-{1}s-logger.hdf".format(self.symbol, self.trade_cycle_time))
            self.prediction = logic.TradePrediction.Prediction("./data/{0}-{1}s-prediction.hdf".format(self.symbol, self.trade_cycle_time))
            self.state = logic.TradeStates.States("./data/{0}-{1}s-states.hdf".format(self.symbol, self.trade_cycle_time))

        self.logger.init_trade_interface(self.api)
        self.state.init_trade_interface(self.api)

    def update(self):
        self.logger.update()
        self.prediction.update(self.logger)
        self.state.update(self.prediction.prediction)

    def save(self):
        if self.simulation == False:
            self.logger.save_storage()
            self.prediction.save_storage()
            self.state.save_storage()
