
class NotImplemented(Exception):
    pass


class State:
    pass


class StateMachine(self):

    def __init__(self):
        self.current_state = BotIdle()

    def next(self, events):
        self.current_state = self.current_state.next(events)


class BotActive(State):

    def next(self, events):
        if events.sell():
            return SellOrder()

        if events.buy():
            return BuyOrder()

        if events.stop():
            return BotIdle()

        return BotActive()


class BotIdle(State):

    def next(self, events):

        if events.start():
            return BotActive()

        return BotIdle()


class BuyAlert(State):

    def next(self, events):

        if events.turning_point():
            return BuyOrder()

        if events.stop():
            return BotIdle()

        return BuyAlert()


class SellAlert(State):

    def next(self, events):
        if events.turning_point():
            return SellOrder()

        if events.stop():
            return BotIdle()

        return SellAlert()


class BuyOrder(State):

    def next(self, events):

        if events.bought():
            return BotActive()

        return BuyOrder()


class SellOrder(State):

    def next(self, events):

        if events.sold():
            return BotActive()

        return SellOrder()
