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
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
    (Transitions.start, false_interface),
]

for _transition, _interface in transitions_stack:
    _transition.set_interface(_interface)

    StateMachines.StateMachine.next(Transitions)

x = 1
