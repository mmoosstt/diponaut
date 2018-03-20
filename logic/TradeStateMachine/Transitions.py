
class Transition(object):

    @classmethod
    def get(clr):
        _result = clr._interface()
        return _result

    @classmethod
    def _interface(clr):
        return False

    @classmethod
    def set_interface(clr, interface):

        clr._interface = interface


class crossed_buy_limit(Transition):
    pass


class corssed_sell_limit(Transition):
    pass


class bought(Transition):
    pass


class sold(Transition):
    pass


class start(Transition):
    pass


class stop(Transition):
    pass


class coins_to_sell(Transition):
    pass


if __name__ == "__main__":
    def interface():

        return "stop"

    stop.set_interface(interface)

    print(stop.get(), start.get())
