from os import path

import moviepy.editor
from pydub import AudioSegment

class InputFile():

	SUPPORTED_TYPES = ["wav",
					"ogg",
					"flv",
					"wma",
					"aac",
					"mp3",

					"mp4",
					"avi",
					"mvk",
					]

	VIDEO_EXT = ["mp4",
				"avi",
				"mvk",
				]

	NO_FILE_SELECTED = 0
	NO_ALLOWED_EXTENSION = 1
	OK_FILE_SELECTED = 2
	GENERIC_ERROR = 3

	def __init__(self, file_name: str):
		""" It handles the input file (audio/video)

		Args:
			file_name (str): file name
		"""

		self.file_name = file_name
		self._file_ext = self.get_extension(file_name)

		self.audio_file_name = None
		self.audio = None

		self.error = None

	def check_selection(self, show_error=True) -> int:
		""" Check if a file is selected or if the format is allowed

		Args:
			file (str): string, selected file, label on "b_selected_file"
		
		Return:
			int: error code. Note that if it's okay, error will be OK_FILE_SELECTED
		"""
		# if audio file is not an allowed format
		ext = self.get_extension(self.file_name)
		if ext not in self.SUPPORTED_TYPES:
			self.error = self.NO_ALLOWED_EXTENSION
		else:
			self.error = self.OK_FILE_SELECTED

		return self.error

	def is_video(self) -> bool:
		""" Check if the file is a video

		Returns:
			bool: True if the file is a video, False otherwise
		"""
		ext = self.file_name[self.file_name.rfind(".")+1:]

		if ext in self.VIDEO_EXT:
			return True
		else:
			return False

	def converting_video(self, output_format="wav") -> AudioSegment:
		""" If chosen file is a video, it will be converted.txt
			After the conversion, set_file is called to load the audio.

		Args:
			output_format (str, optional): in which format the video will be converted.
				Defaults wav.

		Returns:
			AudioSegment: audio object from the file
		"""
		video = moviepy.editor.VideoFileClip(self.file_name)
		audio = video.audio
		output_file = path.join("output",path.basename(self.file_name)[:self.file_name.rfind(".")]+"."+output_format)
		audio.write_audiofile(output_file)

		self.audio = self.get_audio(output_file, output_format)
		return self.audio

	def get_audio(self, file_name=None, audio_type=None) -> AudioSegment:
		""" Get the audio object from the file.

		Args:
			file_name (str, optional): file from which get the audio object. If None, self value will be taken.
				Defaults None.
			audio_type (str, optional): which format is the file. If None, self value will be taken. 
				Defaults to None.

		Returns:
			AudioSegment: audio object from the file
		"""
		if not file_name:
			file_name = self.file_name
		if not audio_type:
			audio_type = self.get_extension(file_name)
		audio = AudioSegment.from_file(file_name, audio_type)
		self.audio_file_name = file_name
		return audio
	
	def get_extension(self, file_name=None) -> str:
		""" Get the extension from the file.

		Args:
			file_name (str, optional): file from which get the extension. If None, self value will be taken.
				Defaults None.

		Returns:
			str: extension
		"""
		if not file_name:
			file_name = self.file_name
		return file_name[file_name.rfind(".") + 1:]

	def get_audio_len(self) -> int:
		""" Get the audio len of the input file.

		Returns:
			int: Audio len. If the audio is no loaded, False.
		"""
		if self.audio:
			return len(self.audio)
		else:
			return False