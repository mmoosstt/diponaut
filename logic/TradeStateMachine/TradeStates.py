
class NotImplemented(Exception):
    pass


class State:

    def __init__(self):
        self.entry()

    def execute(self):
        pass

    def entry(self):
        print(self.__class__.__name__)


class Transition(object):

    def __init__(self):
        self._value = False

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


class Transitions(object):

    def __init__(self):
        self.crossed_buy_limit1 = Transition()
        self.corssed_sell_limit1 = Transition()
        self.turning_point = Transition()
        self.bought = Transition()
        self.sold = Transition()
        self.start = Transition()
        self.stop = Transition()
        self.coins_to_sell = Transition()


class StateMachine(object):

    def __init__(self):
        self.current_state = BotIdle()

    def next(self, transitions):

        self.current_state = self.current_state.next(transitions)
        self.current_state.execute()


class Start(State):

    def next(self, transitions):
        if transitions.sell.get():
            return SellAlert()

        if transitions.buy.get():
            return BuyAlert()

        if transitions.stop.get():
            return BotIdle()

        return self


class Idle(State):

    def next(self, transitions):

        if transitions.start.get():
            return BotActive()

        return self


class BuyAlert(State):

    def next(self, transitions):

        if transitions.turning_point.get():
            return BuyOrder()

        if transitions.stop.get():
            return BotIdle()

        return self


class SellAlert(State):

    def next(self, transitions):
        if transitions.turning_point.get():
            return SellOrder()

        if transitions.stop.get():
            return BotIdle()

        return self


class BuyOrder(State):

    def next(self, transitions):

        if transitions.bought.get():
            return BotActive()

        return self


class SellOrder(State):

    def next(self, transitions):

        if transitions.sold.get():
            return BotActive()

        return self


class WaitForBuy(State):

    def next(self, transitions):

        if transitions.crossing_buy_limit.get():
            return BuyAlert()

        return self


class WaitForSell(State):

    def next(self, transitions):

        if transitions.crossing_sell_limit.get():
            return SellAlert()

        return self

if __name__ == "__main__":

    _transition_stack = [("start", False),
                         ("start", True),
                         ("stop", False),
                         ("stop", True),
                         ("start", True),
                         ("buy", True),
                         ("turning_point", True),
                         ("bought", True),
                         ("stop", True)]

    _state_machine = StateMachine()

    for _m, _v in _transition_stack:

        _transitions = Transitions()
        _transitions.__dict__[_m].set(_v)
        _state_machine.next(_transitions)
