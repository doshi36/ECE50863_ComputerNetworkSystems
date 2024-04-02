# Description: Implementation of the BBA2 algorithm

class BBA2:
    def __init__(self, buffer_size, res_sizes):
        self.buffer_size = buffer_size
        self.res_sizes = res_sizes
        self.buffer_contents = 0

    def get_rate(self):
        if self.buffer_contents < self.buffer_size / 2:
            return self.res_sizes[0]
        elif self.buffer_contents < self.buffer_size:
            return self.res_sizes[1]
        else:
            return self.res_sizes[2]

    def add_to_buffer(self, size):
        self.buffer_contents += size
        if self.buffer_contents > self.buffer_size:
            self.buffer_contents = self.buffer_size

    def remove_from_buffer(self, size):
        self.buffer_contents -= size
        if self.buffer_contents < 0:
            self.buffer_contents = 0
            
# Assuming the list of video rates is ordered from lowest to highest
VIDEO_RATES = [235, 375, 560, 750, 1050, 1750, 2350, 3000, 4300, 5800]  # Example rates in kbps
R_MAX = max(VIDEO_RATES)
R_MIN = min(VIDEO_RATES)

def rate_plus(rate_prev):
    """Find the next higher rate available from the current rate."""
    higher_rates = [rate for rate in VIDEO_RATES if rate > rate_prev]
    return min(higher_rates) if higher_rates else R_MAX

def rate_minus(rate_prev):
    """Find the next lower rate available from the current rate."""
    lower_rates = [rate for rate in VIDEO_RATES if rate < rate_prev]
    return max(lower_rates) if lower_rates else R_MIN

def bba_0(rate_prev, buf_now, r, cu):
    """
    BBA-0 Algorithm Implementation
    
    :param rate_prev: The previously used video rate.
    :param buf_now: The current buffer occupancy.
    :param r: The size of the reservoir.
    :param cu: The size of the cushion.
    :return: The next video rate.
    """
    # Determine Rate+ (the next higher rate) and Rate- (the next lower rate)
    Rate_plus = rate_plus(rate_prev)
    Rate_minus = rate_minus(rate_prev)

    # Algorithm to choose the next rate based on buffer occupancy
    if buf_now <= r:
        Rate_next = R_MIN
    elif buf_now >= (r + cu):
        Rate_next = R_MAX
    elif buf_now > Rate_plus:
        Rate_next = rate_plus(rate_prev)
    elif buf_now < Rate_minus:
        Rate_next = rate_minus(rate_prev)
    else:
        Rate_next = rate_prev

    return Rate_next

# Example usage of the BBA-0 algorithm
# Initialize with an arbitrary previous rate and buffer occupancy
previous_rate = 1050  # kbps
current_buffer = 120  # seconds
reservoir_size = 90   # seconds
cushion_size = 60     # seconds

# Get the next rate based on the BBA-0 algorithm
next_rate = bba_0(previous_rate, current_buffer, reservoir_size, cushion_size)
print(f"The next video rate should be: {next_rate} kbps")


