from pydub import AudioSegment

class Chunk():

	def __init__(self, number: int, chunk: AudioSegment, filename: str, start: str="00:00:00", end: str="00:00:00"):
		""" It defines a chunk.
		    A chunk is a piece of the audio.

		Args:
			number (int): chunk number, to keep the audio ordered.
			chunk (AudioSegment): piece of the audio
			filename (str): filename of the chunk
			start (str, optional): The chunk' start point of the original audio file. 
				Defaults to "00:00:00".
			end (str, optional): The chunk's end point of the original audio file.
				Defaults to "00:00:00".
		"""
		self._number = number
		self._chunk = chunk
		self._file_name = filename
		self._start = start
		self._end = end
		self._done = False
		self._text = ""

	def __str__(self):
		return ("File: "+str(self._filename)+" Start: "+str(self._start)+" End: "+str(self._end))