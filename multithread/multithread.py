from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import time

class CustomQThread(QThread):
	""" This class allows to easly run a custom function in a qthread.
		It takes as input the targetted function and kwargs.
		Kwargs will setted as instance variables with "exec" function,
		so you can use those to pass arguments.
		Furthermore, a general signal is given to know when the thread has been finished

		Utilization example:
			customqthread = CustomQThread(self, 
							"self.sum(self.a, self.b)",
							a=5, b=7)
			customqthread.start()
			customqthread.qthread_finish_signal.connect(<other>)

	"""
	qthread_finish_signal = pyqtSignal()

	def __init__(self, context, function: str, **kwargs):
		""" Read the class detail

		Args:
			context (object): who called
			function (str): function to run
		"""
		QThread.__init__(self, context)
		self._context = context
		self._function = function
		for k,v in kwargs.items():
			exec("self."+k+"=v")

	def run(self):
		eval(self._function)
		self.qthread_finish_signal.emit()

class TimerQThread(QThread):
	""" This class sends a signal every a while.
	    It is basically implemented as a timer.
	"""

	qthread_timer_signal = pyqtSignal()

	def __init__(self, context, seconds=1):
		""" Read the class detail

		Args:
			context (object): who called
			seconds (int): emits signal every tot seconds
		"""
		QThread.__init__(self, context)
		self.seconds = seconds
		self.stopped = False

	def stop(self):
		self.stopped = True

	def run(self):
		self.stopped = False
		while not self.stopped:
			time.sleep(self.seconds)
			self.qthread_timer_signal.emit()
	