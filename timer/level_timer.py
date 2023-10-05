import time


# Initialize a Timer object on game start
# Reuse object for each level
class Timer:
    def __init__(self):
        self.total_time = 0
        self.start_time = 0

    # Call run_timer at level start
    def start_timer(self):
        self.start_time = time.time()

    # Call stop_timer for both pausing and ending a level
    def stop_timer(self):
        current_time = time.time()
        self.total_time += (current_time - self.start_time)

    # Call reset_timer before starting a new level
    def reset_timer(self):
        self.__init__()

    # Call for time
    def return_time(self):
        return self.total_time
