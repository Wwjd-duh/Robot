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
        print("Transition: BOOT")
        self.transition(State.IDLE)

    def transition(self, new_state):
        print(f"Transition: {self.state.name} → {new_state.name}")
        self.state = new_state

    def get_state(self):
        return self.state
