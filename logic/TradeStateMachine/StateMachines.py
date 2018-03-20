import logic.TradeStateMachine.States as States


class StateMachine(object):

    last_state = States.NoState
    current_state = States.Idle

    @classmethod
    def next(cls, transitions):

        cls.current_state = cls.current_state.next(transitions)

        if cls.current_state != cls.last_state:
            cls.last_state.exit()
            cls.current_state.entry()

        # cls.current_state.execute()

        cls.last_state = cls.current_state