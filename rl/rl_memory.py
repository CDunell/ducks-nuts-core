from collections import deque
import random

class RLMemory:
    def __init__(self, capacity=1000):
        self.buffer = deque(maxlen=capacity)

    def append(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size=32):
        return random.sample(self.buffer, min(len(self.buffer), batch_size))

    def clear(self):
        self.buffer.clear()

    def __len__(self):
        return len(self.buffer)