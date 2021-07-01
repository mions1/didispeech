from os import path

import PyQt6.QtWidgets as qt

class SelectFileDialog(qt.QWidget):

	# what return when the dialog has been closed
	NO_FILE_SELECTED = 0
	NO_ALLOWED_EXTENSION = 1
	OK_FILE_SELECTED = 2
	GENERIC_ERROR = 3


	def __init__(self, file_types: list=["*"], title: str="Choose audio file"):
		""" This class handle a file dialog window. So, it lets you choose files
		    browsing into the filesystem

		Args:
			file_types (list, optional): Which file extensions you want to see. Defaults is All files.
				(es. ["wav", "mp3", "mp4"])
			title (str, optional): Title of dialog window. Defaults to "Choose audio file".
		"""
		super().__init__()

		self._file_types = file_types
		self._file_types_str = self.get_file_types_str()
		self._title = title
		self.selected = None
		self.error = None


	def show(self) -> str:
		""" Show the dialog

		Return:
			[int, selected_files]: It returns error code and selected_files list.
		"""
		dialog = qt.QFileDialog(self, self._title, filter=self._file_types_str)
		dialog.exec()
		error = self.check_selection(dialog.selectedFiles())

		if error != self.NO_FILE_SELECTED:
			self.selected = dialog.selectedFiles()[0]
		
		return error, dialog.selectedFiles()
		
	def check_selection(self, select_files: list) -> int:
		""" Check if a file is selected or if the format is allowed

		Args:
			select_files (list): Selected files from dialog
		
		Return:
			int: error generated. Note that if it's ok, error is OK_FILE_SELECT

		"""
		# if no file selected, return
		if len(select_files) == 0:
			self.error = self.NO_FILE_SELECTED

		# if audio file is not an allowed format
		else:
			selected_file = select_files[0]
			ext = selected_file[selected_file.rfind(".") + 1:]
			if ext not in self._file_types \
				and len(self._file_types) > 0 and\
				self._file_types[0] != "*":
				self.error = self.NO_ALLOWED_EXTENSION
			else:
				self.error = self.OK_FILE_SELECTED
		
		return self.error

	def get_file_types_str(self) -> str:
		""" Get the string which is requested to properly show only the files
		    with the wanted extension

		Returns:
			str: string to pass to dialog constructor
		"""
		
		all_supported = "All supported format ("
		file_types = []
		for file_type in self._file_types:
			file_types.append(str(file_type) + " files " + "(*." + str(file_type) + ")")
			all_supported += ("*." + file_type + " ")
		all_supported += ")"
		file_types.insert(0, all_supported)

		file_types_str = ""
		for file_type in file_types:
			file_types_str += file_type+(";;")

		return file_types_str

