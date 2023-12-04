import time
import ntplib


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


class CompetitiveTimer:
    def __init__(self):
        self.total_time = 0
        self.start_time = 0
        self.servers = ['time.nist.gov', 'time.google.com', 'time.windows.com', 'pool.ntp.org', 'north-america.pool.ntp.org']
        self.client = ntplib.NTPClient()

    # Call run_timer at level start
    def start_timer(self):
        if len(self.servers) == 0:
            self.servers = ['time.nist.gov', 'time.google.com', 'time.windows.com', 'pool.ntp.org', 'north-america.pool.ntp.org']
        server_copy = self.servers.copy()

        for server in self.servers:
            try:
                self.start_time = self.client.request(server).tx_time
                self.servers = server_copy
                return True
            except:
                server_copy.remove(server)
        return False

    # Call stop_timer for both pausing and ending a level
    def stop_timer(self):
        if len(self.servers) == 0:
            self.servers = ['time.nist.gov', 'time.google.com', 'time.windows.com', 'pool.ntp.org', 'north-america.pool.ntp.org']
        server_copy = self.servers.copy()

        for server in self.servers:
            try:
                current_time = self.client.request(server).tx_time
                self.total_time += (current_time - self.start_time)
                self.servers = server_copy
                return True
            except:
                server_copy.remove(server)
        return False

    # Call reset_timer before starting a new level
    def reset_timer(self):
        print("resetting")
        self.__init__()

    # Call for time
    def return_time(self):
        return self.total_time
