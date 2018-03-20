
class State(object):

    @classmethod
    def set_execute(cls, interface):
        cls.execute = interface

    @classmethod
    def execute(cls):
        print("execute", cls.__name__)

    @classmethod
    def set_entry(cls, interface):
        cls.entry = interface

    @classmethod
    def entry(cls):
        print("entry", cls.__name__)

    @classmethod
    def set_exit(cls, interface):
        cls.exit = interface

    @classmethod
    def exit(cls):
        print("exit", cls.__name__)

    @classmethod
    def set_next(cls, interface):
        cls.next = interface

    @classmethod
    def next(cls, transitions):
        return cls


class NoState(State):
    pass


class Start(State):

    @classmethod
    def next(cls, transitions):
        if transitions.sell.get():
            return SellAlert()

        if transitions.buy.get():
            return BuyAlert()

        if transitions.stop.get():
            return BotIdle()

        return cls


class Idle(State):

    @classmethod
    def next(cls, transitions):

        if transitions.start.get():
            return Start

        return cls


class BuyAlert(State):

    @classmethod
    def next(cls, transitions):

        if transitions.turning_point.get():
            return BuyOrder()

        if transitions.stop.get():
            return Idle()

        return cls


class SellAlert(State):

    @classmethod
    def next(cls, transitions):
        if transitions.turning_point.get():
            return SellOrder()

        if transitions.stop.get():
            return Idle()

        return cls


class BuyOrder(State):

    @classmethod
    def next(cls, transitions):

        if transitions.bought.get():
            return WaitForSell()

        return cls


class SellOrder(State):

    @classmethod
    def next(cls, transitions):

        if transitions.sold.get():
            return WaitForBuy()

        return cls


class WaitForBuy(State):

    @classmethod
    def next(cls, transitions):

        if transitions.crossing_buy_limit.get():
            return BuyAlert()

        return cls


class WaitForSell(State):

    @classmethod
    def next(cls, transitions):

        if transitions.crossing_sell_limit.get():
            return SellAlert()

        return cls


if __name__ == "__main__":

    import logic.TradeStateMachine.Transitions as transitions

    for x in range(5):
        StateMachine.next(transitions)
    x = 1
