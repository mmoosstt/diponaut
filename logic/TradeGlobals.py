import utils.Interfaces
import re
import time

GloVar = utils.Interfaces.IVariables()

GloVar.actual_price = utils.Interfaces.IVariable(value=0.0, type=float)
GloVar.actual_time = utils.Interfaces.IVariable(value=time.strftime("%H:%M:%S"), type=str)

GloVar.path_storage = utils.Interfaces.IVariable(value="./data_storage", type=str, protected=True)
GloVar.path_temp = utils.Interfaces.IVariable(value="./data_temp", type=str, protected=True)
GloVar.path_config = utils.Interfaces.IVariable(value="./config", type=str, protected=True)

GloVar.trade_symbol = utils.Interfaces.IVariable(value="TRXETH", type=str, protected=False)
GloVar.trade_quantity = utils.Interfaces.IVariable(value=250, type=int, protected=True)
GloVar.trade_simulation = utils.Interfaces.IVariable(value=False, type=bool, protected=True)
GloVar.trade_sample_time = utils.Interfaces.IVariable(value=10., type=float, protected=True)

GloVar.factor_buy_offset = utils.Interfaces.IVariable(value=2.01, type=float)
GloVar.factor_sell_offset = utils.Interfaces.IVariable(value=0.99, type=float)

GloVar.filt1_hz = utils.Interfaces.IVariable(value=0.01, type=float)
GloVar.filt1_grad_range = utils.Interfaces.IVariable(value=6, type=int)
GloVar.filt1_grad = utils.Interfaces.IVariable(value=0., type=float)

GloVar.filt2_hz = utils.Interfaces.IVariable(value=0.001, type=float)
GloVar.filt2_grad_range = utils.Interfaces.IVariable(value=300, type=int)
GloVar.filt2_grad = utils.Interfaces.IVariable(value=0., type=float)

GloVar.state = utils.Interfaces.IVariable(value="DoNothing", type=str)
GloVar.state_buy_time = utils.Interfaces.IVariable(value=0., type=int)
GloVar.state_buy_price = utils.Interfaces.IVariable(value=0., type=float)
GloVar.state_sell_time = utils.Interfaces.IVariable(value=0, type=int)
GloVar.state_sell_price = utils.Interfaces.IVariable(value=0., type=float)
GloVar.state_zero_crossing_time = utils.Interfaces.IVariable(value=0, type=int)
GloVar.state_zero_crossing_price = utils.Interfaces.IVariable(value=0., type=float)

GloVar.state_sell_lost_limit = utils.Interfaces.IVariable(value=-1.4e10, type=float)
GloVar.state_sell_win_limit = utils.Interfaces.IVariable(value=1.4e10, type=float)


GloVar.order_delta_price = utils.Interfaces.IVariable(value=0., type=float)

GloVar.SaveTimeOffset = utils.Interfaces.IVariable(value=0.0, type=float, protected=True)

GloVar.cyclic_task_main = utils.Interfaces.IVariable(value=10., type=float, protected=True)
GloVar.cyclic_task_plotting = utils.Interfaces.IVariable(value=30., type=float, protected=True)
GloVar.cyclic_task_store = utils.Interfaces.IVariable(value=60., type=float, protected=True)


def _loadArguments(args):
    """
    analys argv with out own signal name
    structure of arguments -<GloVarName>:<GloVarValue>
    example:
    python.exe diponaut.py -trade_symbol:TRXETH

    """

    for arg in args:

        _res = re.findall("-(.*):(.*)", arg)

        if _res != []:
            if len(_res[0]) == 2:

                GloVarName = _res[0][0]
                GloVarValue = _res[0][1]

                if GloVarName in GloVar.__dict__.keys():
                    GloVar.set(GloVarName, GloVarValue)
                    print(GloVarName, GloVarValue)


GloVar.loadArguments = _loadArguments


if __name__ == "__main__":

    def test(eins, zwei):
        print(eins, zwei.value, zwei.name)

    GloVar.signal_set.connect(test)
    GloVar.emit_all()
