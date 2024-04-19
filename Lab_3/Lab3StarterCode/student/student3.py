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


# Your helper functions, variables, classes here. You may also write initialization routines to be called
# when this script is first imported and anything else you wish.

class BOLA:
	def __init__(self):
		self.current_quality  = 0
		self.m_n_prev 		  = 0
		self.m_n              = 0
		self.estimated_throughput = 0  # Initialize estimated throughput
		self.current_chunk 	  = 0
		self.total_chunks 				= 0 

	def ewma_throughput(self, previous_throughput, alpha=0.80):
		"""
		Exponentially Weighted Moving Average for throughput estimation.
		`alpha` is the weighting factor, closer to 1 gives more weight to recent values.
		"""
		if self.estimated_throughput == 0:  # First time, initialize with the first known throughput
			self.estimated_throughput = previous_throughput
		else:
			self.estimated_throughput = alpha * previous_throughput + (1 - alpha) * self.estimated_throughput
		return self.estimated_throughput
  
	def get_quality(self, client_message: ClientMessage):
		self.quality_bitrates 			= client_message.quality_bitrates
		self.buffer_seconds_until_empty = client_message.buffer_seconds_until_empty
		self.buffer_seconds_per_chunk 	= client_message.buffer_seconds_per_chunk
		self.quality_levels 			= client_message.quality_levels
		self.total_seconds_elapsed 		= client_message.total_seconds_elapsed
		self.buffer_max_size 			= client_message.buffer_max_size
		self.upcoming_quality_bitrates  = client_message.upcoming_quality_bitrates
		self.previous_throughput 		= client_message.previous_throughput
		self.quality_max 				= client_message.quality_coefficient * (client_message.quality_levels - 1)
		self.gamma 						= client_message.rebuffering_coefficient/self.buffer_seconds_per_chunk
		self.current_chunk 				+= 1
		self.total_chunks 				= len(self.upcoming_quality_bitrates) + 1 if len(self.upcoming_quality_bitrates) > self.total_chunks else self.total_chunks
		self.quality_coefficient		= client_message.quality_coefficient
  
		return self.calculate_bola()
	
	def max_utility_check(self,v_d):
     
		max_utility = float('-inf')
		max_quality = 0
		p = self.buffer_seconds_per_chunk
  
		for i, S_m in enumerate(self.quality_bitrates):
			run_value = ((self.quality_coefficient*i * v_d) + (v_d * self.gamma * p) - self.buffer_seconds_until_empty) / S_m
   
			if run_value > max_utility:
				max_utility = run_value
				max_quality = i
    
		return max_quality

	def find_max_quality(self,r):
     
		p = self.buffer_seconds_per_chunk
		S_1 = self.quality_bitrates[0]
		max_val = max(r, S_1/p)

		return max(list(m for m in range(self.quality_levels) if self.quality_bitrates[m]/p <= max_val))

	def calculate_bola(self):
		p = self.buffer_seconds_per_chunk
		t = min(self.current_chunk*p, ((self.total_chunks-self.current_chunk)*p))
		t_prime = max(t/2, 3*p)

		qd_max = min(self.buffer_max_size, t_prime/p)
		v_d = (qd_max - 1) / (self.quality_max + (self.gamma * p))
		self.m_n = self.max_utility_check(v_d)
		self.current_quality = self.m_n
  
		if self.m_n > self.m_n_prev:
			r = self.ewma_throughput(self.previous_throughput)
			m_prime = self.find_max_quality(r)
			if m_prime >= self.m_n:
				m_prime = self.m_n
			elif m_prime < self.m_n_prev:
				m_prime = self.m_n_prev
			self.current_quality = m_prime
   
		self.m_n_prev = self.current_quality
		return self.current_quality

bola = BOLA()

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
 
	quality = bola.get_quality(client_message=client_message)  # Let's see what happens if we select the lowest bitrate every time
	return quality
