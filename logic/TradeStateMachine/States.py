

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


class Idle(State):

    @classmethod
    def next(cls, transitions):

        if transitions.start.get():
            return Start

        return cls


class Start(State):

    @classmethod
    def next(cls, transitions):

        if transitions.stop.get():
            return Idle

        if transitions.coins_to_sell.get():
            return WaitForSell

        else:
            return WaitForBuy

        return cls


class BuyAlert(State):

    @classmethod
    def next(cls, transitions):

        if transitions.stop.get():
            return Idle

        if transitions.turning_point.get():
            return BuyOrder

        return cls


class SellAlert(State):

    @classmethod
    def next(cls, transitions):

        if transitions.stop.get():
            return Idle

        if transitions.turning_point.get():
            return SellOrder

        return cls


class BuyOrder(State):

    @classmethod
    def next(cls, transitions):

        if transitions.stop.get():
            return Idle

        if transitions.bought.get():
            return WaitForSell

        return cls


class SellOrder(State):

    @classmethod
    def next(cls, transitions):

        if transitions.stop.get():
            return Idle

        if transitions.sold.get():
            return WaitForBuy

        return cls


class WaitForBuy(State):

    @classmethod
    def next(cls, transitions):

        if transitions.stop.get():
            return Idle

        if transitions.crossed_buy_limit.get():
            return BuyAlert

        return cls


class WaitForSell(State):

    @classmethod
    def next(cls, transitions):

        if transitions.stop.get():
            return Idle

        if transitions.crossed_sell_limit.get():
            return SellAlert

        return cls
