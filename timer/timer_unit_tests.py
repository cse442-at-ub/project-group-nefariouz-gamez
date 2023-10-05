import unittest
import time
from level_timer import Timer


# These unit tests can only be accurate to 1 decimal point because of the time it takes to run stat_timer and stop_timer
class TestTimer(unittest.TestCase):
    # Test One: Making sure timer works
    def test_one(self):
        timer = Timer()

        # Start timer for 10 seconds
        timer.start_timer()
        time.sleep(3)

        # End timer and check
        timer.stop_timer()
        self.assertTrue(3.00 < timer.return_time() < 3.10)

    # Test Two: Pausing timer once for 2 seconds
    def test_two(self):
        timer = Timer()

        # Start timer for 5 seconds
        timer.start_timer()
        time.sleep(1)

        # Pause for 2 seconds
        timer.stop_timer()
        time.sleep(3)

        # Start timer back up for 5 seconds
        timer.start_timer()
        time.sleep(1)

        # End timer and check
        timer.stop_timer()
        self.assertTrue(2.00 < timer.return_time() < 2.10)

    # Test Three: Pausing timer twice for 2 and 3 seconds
    def test_three(self):
        timer = Timer()

        # Start timer for 3 seconds
        timer.start_timer()
        time.sleep(1)

        # Pause for 2 seconds
        timer.stop_timer()
        time.sleep(2)

        # Start timer back up for 4 seconds
        timer.start_timer()
        time.sleep(1)

        # Pause for 3 seconds
        timer.stop_timer()
        time.sleep(3)

        # Start timer back up for 3 seconds
        timer.start_timer()
        time.sleep(1)

        # End timer and check
        timer.stop_timer()
        self.assertTrue(3.00 < timer.return_time() < 3.10)

    # Test Four: Check that reset_timer works
    def test_four(self):
        timer = Timer()

        # Start timer for 3 seconds
        timer.start_timer()
        time.sleep(3)

        # Reset the timer
        timer.reset_timer()

        # Start timer for 3 seconds
        timer.start_timer()
        time.sleep(1)

        # End timer and check
        timer.stop_timer()
        self.assertTrue(1.00 < timer.return_time() < 1.10)


if __name__ == '__main__':
    unittest.main()
