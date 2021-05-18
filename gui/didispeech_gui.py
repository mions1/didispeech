import threading, os
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg

from os import path

import moviepy.editor
from pydub import AudioSegment

from gui.dialog.select_file import SelectFileDialog
from gui.dialog.message import MessageDialog

from files_management.input_file import InputFile

class DidispeechGui(qt.QGridLayout):
	""" Handle application.
		Create layouts and widgets, connect buttons and
		handle their functions.
	"""

	# default paths
	DEFAULT_RESOURCES_DIR = "resources"
	DEFAULT_IMG_RESOURCES_DIR = path.join(DEFAULT_RESOURCES_DIR, "images")
	DEFAULT_OUTPUT_DIR = "output"
	DEFAULT_INPUT_FILE = "Select file..."
	DEFAULT_OUTPUT_FILE = path.join(DEFAULT_OUTPUT_DIR, "save.txt")
	DEFAULT_LOGO_FILE = path.join(DEFAULT_IMG_RESOURCES_DIR, "title.png")

	def __init__(self, didispeech_app, input_file=DEFAULT_INPUT_FILE, \
		output_file=DEFAULT_OUTPUT_FILE):
		""" Main class, application

		Parameters:
			didispeech_app(DidispeechApp): main application
		"""
		super().__init__()
		self._didispeech_app = didispeech_app

		self._input_file = InputFile(input_file)
		self._output_file = output_file

	def init(self) -> None:
		""" Create layout and widgets like buttons, textbox, etc.
		"""

		# load didispeech logo
		l_title = qt.QLabel()
		pixmap = qtg.QPixmap(self.DEFAULT_LOGO_FILE)
		l_title.setPixmap(pixmap)

		#-------------- Layout select file ----------------------------------------
		self._f_select_file = qt.QGridLayout()

		# select input file (which one to transcribe)
		self._l_select_input_file = qt.QLabel("Input file:")
		self._b_select_input_file = qt.QPushButton(self._input_file.file_name)

		# select output file (where to save the transcription)
		self._l_select_output_file = qt.QLabel("Output file: ")
		self._b_select_output_file = qt.QPushButton(self._output_file)

		# connect buttons to functions
		self._b_select_input_file.clicked.connect(lambda a: self.select_input_file())
		self._b_select_output_file.clicked.connect(lambda a: self.select_output_file())

		# add them all to the layout
		self._f_select_file.addWidget(self._l_select_input_file, 0,0)
		self._f_select_file.addWidget(self._b_select_input_file, 1,0)

		self._f_select_file.addWidget(self._l_select_output_file, 0,1)
		self._f_select_file.addWidget(self._b_select_output_file, 1,1)

		self._f_select_file.addWidget(l_title, 2,0,2,2)
		self._f_select_file.addWidget(self.get_QHline(), 3,0,3,2)

		#-------------- Layout options --------------------------------------------
		self._f_options = qt.QGridLayout()

		# set the transcription start point
		self._l_start = qt.QLabel("Start (hh:mm:ss)")
		self._e_start = qt.QLineEdit()
		self._e_start.setMaxLength(8)
		self._e_start.setInputMask("99:99:99")
		self._e_start.setText("00:00:00")

		# set the transcription end point
		self._l_end = qt.QLabel("End (hh:mm:ss)")
		self._e_end = qt.QLineEdit()
		self._e_end.setMaxLength(8)
		self._e_end.setInputMask("99:99:99")
		self._e_end.setText("00:00:00")

		# buttons to start/quit
		self._b_start = qt.QPushButton("Start", enabled=False, default=True)
		self._b_quit = qt.QPushButton("Force quit")

		self._b_quit.clicked.connect(self._didispeech_app.exit)

		# other settings: FIXME make other settings
		self._b_other_settings = qt.QPushButton("Other settings")

		# add them all to the layout
		self._f_options.addWidget(self._l_start, 0,0)
		self._f_options.addWidget(self._e_start, 0,1)
		self._f_options.addWidget(self._l_end, 1,0)
		self._f_options.addWidget(self._e_end, 1,1)

		self._f_options.addWidget(self._b_start, 2,0)
		self._f_options.addWidget(self._b_quit, 2,1)
		#self._f_options.addWidget(self._b_other_settings, 3,0,3,3)

		#---------- Layout Output ---------------------------------------------
		self._f_output = qt.QVBoxLayout()

		# output box (where write log and result)
		self._tb_out = qt.QTextEdit()
		self._tb_out.setReadOnly(True)
		tmp_str = "1. Select an audio file\n"
		tmp_str += "2. Set range time to parse\n"
		tmp_str += "3. Press Start button\n"
		tmp_str += "In this box you will see log. Result will be saved on output file"
		self.tb_insert(tmp_str, True)

		# add it to the layout
		self._f_output.addWidget(self._tb_out)

		#---------- <ADD HERE OTHER FRAMES AND WIDGETS TO CREATE> -------------

		# add all layout to the main frame
		self.addLayout(self._f_select_file, 0,0)
		self.addLayout(self._f_options, 1,0,1,1)
		self.addLayout(self._f_output, 2,0,2,2)


	def select_input_file(self) -> None:
		""" Browse into filesystem to choose an audio or a video file, then 
			write it as instance variable and as button text

		"""
		select_file_dialog = SelectFileDialog(file_types=InputFile.SUPPORTED_TYPES)
		error, selected_files = select_file_dialog.show()

		if error == SelectFileDialog.OK_FILE_SELECTED:
			self.set_input_file(select_file_dialog.selected)
		elif error == SelectFileDialog.NO_ALLOWED_EXTENSION:
			MessageDialog("Error", "No allowed format", \
				"Format of " + select_file_dialog.selected + " is not allowed", \
				MessageDialog.ICON_CRITICAL)
		elif error == SelectFileDialog.GENERIC_ERROR:
			MessageDialog("Error", "Generic error")
		elif error == SelectFileDialog.NO_FILE_SELECTED:
			MessageDialog("Warning", "No file selected", icon=MessageDialog.ICON_INFORMATION)


	def set_input_file(self, input_file: str) -> None:
		""" Set selected input file as instance variable and as text of b_select_input_file

		Args:
			input_file (str): selected input file
		"""
		self._input_file = InputFile(input_file)
		self._b_select_input_file.setText(path.basename(input_file))

	def select_output_file(self) -> None:
		""" Browse into filesystem to choose where save the transcript, then 
			write it as instance variable and as button text

		"""
		open_file_dialog = SelectFileDialog(title="Save file on...")
		error, selected_files = open_file_dialog.show()

		if error == SelectFileDialog.OK_FILE_SELECTED:
			self.set_output_file(open_file_dialog.selected)
		elif error == SelectFileDialog.NO_ALLOWED_EXTENSION:
			MessageDialog("Error", "No allowed format", \
				"Format of " + select_file_dialog.selected + " is not allowed", \
				MessageDialog.ICON_CRITICAL)
		elif error == SelectFileDialog.GENERIC_ERROR:
			MessageDialog("Error", "Generic error")
		elif error == SelectFileDialog.NO_FILE_SELECTED:
			MessageDialog("Warning", "No file selected", icon=MessageDialog.ICON_INFORMATION)

	def set_output_file(self, output_file: str) -> None:
		""" Set selected output file as instance variable and as text of b_select_output_file

		Args:
			output_file (str): selected output file
		"""
		self._output_file = output_file
		self._b_select_output_file.setText(path.basename(output_file))

	def tb_insert(self, text, replace=False) -> None:
		""" Insert a text into output textbox

		Args:
			text (str): text to write into Textbox
			replace (bool, optional): If true, replace current text, 
				otherwise append the new text to it. Defaults to False.
		"""
		if replace:
			self._tb_out.setText(text)
		else:
			self._tb_out.append(text)

	def tb_get_text(self) -> str:
		""" Get the current text in output textbox.

		Returns:
			str: text of output textbox
		"""
		return self._tb_out.toPlainText()

	def get_QHline(self) -> qt.QFrame:
		""" Return a horizontal line, aestetich purpouse.Q

		Returns:
			qt.QFrame: a horizontal line
		"""
		qhline = qt.QFrame()
		qhline.setFrameShape(qt.QFrame.HLine)
		qhline.setFrameShadow(qt.QFrame.Plain)
		return qhline