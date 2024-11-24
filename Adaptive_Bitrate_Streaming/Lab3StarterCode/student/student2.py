# Name: Parth R. Doshi, 	Email ID: doshi36@purdue.edu
# Name: Vignesh Charapalli, Email ID: vcharapa@purdue.edu
# ABR Algorithm: BBA-2

from typing import List

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


class BBA_2:
	def  __init__(self):
		self.rate_prev 	  = 0
		self.quality_prev = 0
		self.reservoir 	  = 11
		self.cushion   	  = 16
		self.X    = 60 
		self.change_bandwidth = 0
		self.previous_buffer = 0
			
	def adjust_buffer(self):
		slope 		  = (self.rate_max - self.rate_min) / (self.cushion)
		expected_rate = self.rate_min + slope * (self.buffer_seconds_until_empty - self.reservoir)
		return expected_rate

	def adjust_reservoir(self):
		adjustment = 0
		pos_vals = 0
		neg_vals = 0
		idx = 0

		for idx, val in enumerate(self.upcoming_quality_bitrates):
			pos_vals += val[self.quality_prev]
			if idx >= self.X:
				break
		if idx != 0:
			neg_vals = self.previous_throughput * idx
			adjustment = pos_vals - neg_vals
			self.reservoir += adjustment/(idx*3)
			
			if self.reservoir < 0:
				self.reservoir = 0
    
	def get_quality(self,client_message: ClientMessage):
		self.quality_bitrates 			= client_message.quality_bitrates
		self.buffer_seconds_until_empty = client_message.buffer_seconds_until_empty
		self.buffer_seconds_per_chunk 	= client_message.buffer_seconds_per_chunk
		self.quality_levels 			= client_message.quality_levels
		self.total_seconds_elapsed 		= client_message.total_seconds_elapsed
		self.rate_prev 					= client_message.quality_bitrates[self.quality_prev]
		self.buffer_max_size 			= client_message.buffer_max_size
		self.upcoming_quality_bitrates  = client_message.upcoming_quality_bitrates
		self.previous_throughput 		= client_message.previous_throughput
		self.rate_max = self.quality_bitrates[-1]
		self.rate_min = self.quality_bitrates[0]
		self.adjust_reservoir()
		# print("Reservoir: ",self.reservoir)
		rate_plus  = self.rate_plus()
		rate_minus = self.rate_minus()
		self.expected_rate = self.adjust_buffer()
		self.change_bandwidth = self.buffer_seconds_per_chunk - self.previous_buffer
		self.previous_buffer = self.buffer_seconds_per_chunk
		if client_message.buffer_seconds_until_empty <= self.reservoir:
			# if self.change_bandwidth > 0.1*self.buffer_seconds_per_chunk: # Better without startup
			# 	rate_next = rate_plus
			# else:
			rate_next = self.rate_min
		elif client_message.buffer_seconds_until_empty >= (self.reservoir + self.cushion):
			rate_next = self.rate_max
		elif self.expected_rate >= rate_plus:
			rate_next = max([rate for rate in self.quality_bitrates if rate < self.expected_rate])
		elif self.expected_rate <= rate_minus:
			rate_next = min([rate for rate in self.quality_bitrates if rate > self.expected_rate])
		else:
			rate_next = self.rate_prev

		self.rate_prev = rate_next
		quality_next = self.quality_bitrates.index(rate_next)
		self.quality_prev = quality_next
  
		return quality_next
   
	def rate_plus(self):
		if self.quality_prev == self.quality_levels - 1:
			return self.rate_max
		else:
			return min([rate for rate in self.quality_bitrates if rate > self.rate_prev])

	def rate_minus(self):
		if self.quality_prev == 0:
			return self.rate_min
		else:
			return max([rate for rate in self.quality_bitrates if rate < self.rate_prev])


global bba_class
bba_class = BBA_2()

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
 
	return bba_class.get_quality(client_message)