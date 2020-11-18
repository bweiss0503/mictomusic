from threading import Thread, Event


# class for stoppable thread
# runs record while active and finalize_wav upon termination
class RecordController(object):
	def __init__(self, listen):
		self.l_instance = listen
		self.thread = None
		self.stop_threads = Event()

	def loop(self):
		while not self.stop_threads.is_set():
			self.l_instance.record()

	def start(self):
		self.stop_threads.clear()
		self.thread = Thread(target=self.loop)
		self.thread.start()

	def stop(self):
		self.stop_threads.set()
		self.thread.join()
		self.thread = None
		self.l_instance.finalize_wav()
