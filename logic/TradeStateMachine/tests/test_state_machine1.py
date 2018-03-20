import logic.TradeStateMachine.Transitions as Transitions
import logic.TradeStateMachine.StateMachines as StateMachines


def true_interface():
    return True


def false_interface():
    return False


transitions_stack = [
    (Transitions.start, false_interface),
    (Transitions.start, true_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.crossed_buy_limit, true_interface),
    (Transitions.crossed_buy_limit, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.turning_point, true_interface),
    (Transitions.turning_point, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.bought, true_interface),
    (Transitions.bought, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.crossed_sell_limit, true_interface),
    (Transitions.crossed_sell_limit, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.turning_point, true_interface),
    (Transitions.turning_point, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.sold, true_interface),
    (Transitions.sold, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.stop, true_interface),
    (Transitions.stop, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
]

for _transition, _interface in transitions_stack:
    _transition.set_interface(_interface)

    StateMachines.StateMachine.next(Transitions)

x = 1
