from typing import List
import statistics
from itertools import product
# Adapted from code by Zach Peats

# ======================================================================================================================
# Do not touch the client message class!
# ======================================================================================================================


class ClientMessage:
	"""
	This class will be filled out and passed to student_entrypoint for your algorithm.
	"""
	total_seconds_elapsed: float	  # The number of simulated seconds elapsed in this test
	previous_throughput: float		  # The measured throughput for the previous chunk in kB/s

	buffer_current_fill: float		    # The number of kB currently in the client buffer
	buffer_seconds_per_chunk: float     # Number of seconds that it takes the client to watch a chunk. Every
										# buffer_seconds_per_chunk, a chunk is consumed from the client buffer.
	buffer_seconds_until_empty: float   # The number of seconds of video left in the client buffer. A chunk must
										# be finished downloading before this time to avoid a rebuffer event.
	buffer_max_size: float              # The maximum size of the client buffer. If the client buffer is filled beyond
										# maximum, then download will be throttled until the buffer is no longer full

	# The quality bitrates are formatted as follows:
	#
	#   quality_levels is an integer reflecting the # of quality levels you may choose from.
	#
	#   quality_bitrates is a list of floats specifying the number of kilobytes the upcoming chunk is at each quality
	#   level. Quality level 2 always costs twice as much as quality level 1, quality level 3 is twice as big as 2, and
	#   so on.
	#       quality_bitrates[0] = kB cost for quality level 1
	#       quality_bitrates[1] = kB cost for quality level 2
	#       ...
	#
	#   upcoming_quality_bitrates is a list of quality_bitrates for future chunks. Each entry is a list of
	#   quality_bitrates that will be used for an upcoming chunk. Use this for algorithms that look forward multiple
	#   chunks in the future. Will shrink and eventually become empty as streaming approaches the end of the video.
	#       upcoming_quality_bitrates[0]: Will be used for quality_bitrates in the next student_entrypoint call
	#       upcoming_quality_bitrates[1]: Will be used for quality_bitrates in the student_entrypoint call after that
	#       ...
	#
	quality_levels: int
	quality_bitrates: List[float]
	upcoming_quality_bitrates: List[List[float]]

	# You may use these to tune your algorithm to each user case! Remember, you can and should change these in the
	# config files to simulate different clients!
	#
	#   User Quality of Experience =    (Average chunk quality) * (Quality Coefficient) +
	#                                   -(Number of changes in chunk quality) * (Variation Coefficient)
	#                                   -(Amount of time spent rebuffering) * (Rebuffering Coefficient)
	#
	#   *QoE is then divided by total number of chunks
	#
	quality_coefficient: float
	variation_coefficient: float
	rebuffering_coefficient: float
# ======================================================================================================================

class RobustMPC:
	def __init__(self):
		self.prev_throughputs = []
		self.pred_throughputs = []
		self.prev_qualities   = []
		self.current_chunk = 0
		self.W = 5
		self.quality_prev = 0
	
	def pred_error_throughput(self):
		if self.previous_throughput == 0:
			self.prev_throughputs += [2]
			self.pred_throughputs += [2]
			return
		
		self.prev_throughputs += [self.previous_throughput]
		error = 0
		if len(self.pred_throughputs) < self.W:
			self.pred_throughputs+= [self.previous_throughput]
			return
		
		mean = statistics.harmonic_mean(self.prev_throughputs[-self.W:])

		for idx in range(self.W):
			error += abs((self.prev_throughputs[-idx] - self.pred_throughputs[-idx])/self.prev_throughputs[-idx])
		error = error/self.W

		self.pred_throughputs.append(mean/(1+error))

	def calculate_qoe(self,combos):
		predicted_throughput = self.pred_throughputs[-1]
		quality_sum = 0
		buffer_sum = 0
		variant_sum = 0
		buffer_sum = self.buffer_seconds_until_empty
		for idx in range(len(combos)):
			if self.buffer_seconds_until_empty < 11:
				buffer_sum -= 11
			quality_sum += combos[idx]
			buffer_sum -= ((self.upcoming_quality_bitrates[idx][combos[idx]]/predicted_throughput))
			if idx != len(combos) - 1:
				variant_sum += abs((combos[idx + 1] - combos[idx]))
		
		return self.quality_coefficient*quality_sum-self.variation_coefficient*variant_sum+(self.rebuffering_coefficient)*(buffer_sum)

	def get_qoe(self): 
		numbers = [i for i in range(self.quality_levels)]
		combos = list(product(numbers, repeat=self.W) if len(self.upcoming_quality_bitrates) >= self.W else product(numbers, repeat=len(self.upcoming_quality_bitrates)))
		max_qoe = -999
		qoe_idx = 0
		for idx in range(len(combos)):
			qoe = self.calculate_qoe(combos[idx])
			if qoe > max_qoe:
				max_qoe = qoe
				qoe_idx = idx
		if max_qoe == -999:
			return 0
		if combos[qoe_idx] == ():
			return self.prev_qualities[-1]
		return combos[qoe_idx][0]
	

	def get_quality(self, client_message: ClientMessage):
		self.quality_bitrates 			= client_message.quality_bitrates
		self.buffer_seconds_until_empty = client_message.buffer_seconds_until_empty
		self.buffer_seconds_per_chunk 	= client_message.buffer_seconds_per_chunk
		self.quality_levels 			= client_message.quality_levels
		self.total_seconds_elapsed 		= client_message.total_seconds_elapsed
		self.rate_prev 					= client_message.quality_bitrates[self.quality_prev]
		self.buffer_max_size 			= client_message.buffer_max_size
		self.upcoming_quality_bitrates  = client_message.upcoming_quality_bitrates
		self.previous_throughput 		= client_message.previous_throughput
		self.quality_coefficient = client_message.quality_coefficient
		self.variation_coefficient = client_message.variation_coefficient
		self.rebuffering_coefficient = client_message.rebuffering_coefficient/2.7
		self.upcoming_quality_bitrates = client_message.upcoming_quality_bitrates

		self.pred_error_throughput()
		qoe_returned = self.get_qoe()
		self.prev_qualities += [qoe_returned]
		return qoe_returned


# Your helper functions, variables, classes here. You may also write initialization routines to be called
# when this script is first imported and anything else you wish.
global mpc_class
mpc_class = RobustMPC()

def student_entrypoint(client_message: ClientMessage):
	"""
	Your mission, if you choose to accept it, is to build an algorithm for chunk bitrate selection that provides
	the best possible experience for users streaming from your service.

	Construct an algorithm below that selects a quality for a new chunk given the parameters in ClientMessage. Feel
	free to create any helper function, variables, or classes as you wish.

	Simulation does ~NOT~ run in real time. The code you write can be as slow and complicated as you wish without
	penalizing your results. Focus on picking good qualities!

	Also remember the config files are built for one particular client. You can (and should!) adjust the QoE metrics to
	see how it impacts the final user score. How do algorithms work with a client that really hates rebuffering? What
	about when the client doesn't care about variation? For what QoE coefficients does your algorithm work best, and
	for what coefficients does it fail?

	Args:
		client_message : ClientMessage holding the parameters for this chunk and current client state.

	:return: float Your quality choice. Must be one in the range [0 ... quality_levels - 1] inclusive.
	"""
	return mpc_class.get_quality(client_message=client_message)
	# Let's see what happens if we select the lowest bitrate every time
