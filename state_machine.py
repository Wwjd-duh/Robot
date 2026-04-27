# this is the state machine
from enum import Enum


class State(Enum):
    BOOT = 0
    IDLE = 1
    IN_SCOPE = 2
    EXEC_ACTIONS = 3


class StateMachine:

    def __init__(self):

        self.state = State.BOOT
        self.callbacks = []

        print("STATE MACHINE START")
        print("Current State:", self.state.name)

        self.transition(State.IDLE)

    # --------------------------------------------------
    # STATE TRANSITION
    # --------------------------------------------------

    def transition(self, new_state):

        # Prevent redundant transitions
        if new_state == self.state:
            return

        old_state = self.state
        self.state = new_state

        print(f"STATE CHANGE: {old_state.name} -> {new_state.name}")

        # Notify any listeners
        for callback in self.callbacks:
            callback(old_state, new_state)

    # --------------------------------------------------
    # GET CURRENT STATE
    # --------------------------------------------------

    def get_state(self):
        return self.state

    # --------------------------------------------------
    # CHECK STATE
    # --------------------------------------------------

    def is_state(self, state):
        return self.state == state

    # --------------------------------------------------
    # REGISTER CALLBACKS
    # --------------------------------------------------

    def register_callback(self, callback):
        self.callbacks.append(callback)