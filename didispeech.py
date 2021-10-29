#import PyQt5.QtWidgets as qt
import PyQt6.QtWidgets as qt


from gui.didispeech_gui import DidispeechGui

class DidispeechApp(qt.QApplication):
	""" Handle application.
		This is the application.
	"""

	def __init__(self):
		""" Main class, application

		"""
		super().__init__(["DidispeechApp"])
		self._window = qt.QFrame()

	def repaint(self, frame: qt.QLayout):
		""" Repaint the gui with the selected frame.
			It sets as window layout the selected frame.

		Args:
			frame (qt.QLayout): an arbitrary layout
		"""
		self._window = qt.QFrame()
		self._window.resize(700, 500)
		self._window.setLayout(frame)
		self._window.show()	

if __name__=='__main__':
	
	# create and show app window
	didispeech_app = DidispeechApp()

	didispeech_gui = DidispeechGui(didispeech_app)
	didispeech_gui.init()

	didispeech_app.repaint(didispeech_gui)
	didispeech_app.exec()