import speech_recognition as sr
import os, time, sys

from pydub import AudioSegment

from threading import Thread
from files_management.input_file import InputFile

from core.chunk import Chunk

class Didi:

    THREADS = 8

    def __init__(self, context, input_file: InputFile=None, ms_start=0, ms_end=0, output_file="save.txt", chunk_size=50000, lan="it-IT"):
        self.init(context, input_file, ms_start, ms_end, output_file, lan)

    def init(self, context, input_file: InputFile=None, ms_start=0, ms_end=0, output_file="save.txt", lan="it-IT", chunk_size=50000, output_text=None, elapsed_time=None):
        self.context = context
        self.input_file = input_file
        self.ms_start = ms_start
        self.ms_end = ms_end
        self.output_file = output_file
        self.lan = lan

        # maximum length allowed by google is 60sec
        self.chunk_size = chunk_size
        if chunk_size > 60000:
            self.chunk_size = 60000
        elif chunk_size < 1000:
            self.chunk_size = 1000

        self.chunks = []
        self.done_chunks = []
        self.parsing_threads = []

        self.output_text = output_text
        self.elapsed_time = elapsed_time

    def start(self) -> None:
        """ Start the procedure to trancript
        """
        # 0. check input and convert in audio
        if not self.input_file.audio:
            self.load_audio()

        # 1. split in chunks
        self.create_chunks(prefix=self.input_file.audio_file_name)

        # 2. start parsing
        self.start_parsing()

    def load_audio(self) -> AudioSegment:
        """ Get the audio object from the InputFile

        Returns:
            AudioSegment: audio from the input file
        """
        file_type = self.input_file.check_selection()
        if not file_type:
            return False
            
        if self.input_file.is_video():
            self.input_file.audio = self.input_file.converting_video()
        else:
            self.input_file.audio = self.input_file.get_audio(self.input_file.file_name)

        return self.input_file.audio

    def create_chunks(self, prefix: str=None, chunk_size: int=None) -> None:
        """ Divide the audio in chunks, so they can be processed in parallel.
            Every chunk will be a file named like "<prefix>_chunck_<i>.<ext>".
            self.chunks list will be filled with these chunks.

        Args:
            prefix (str, optional): Name to give to the chunks. It it is None, input_file_name will be. 
                Defaults to None.
            chunk_size (int, optional): How many milliseconds for any chunk. If none, self value will be taken. 
                Defaults to None.
        """
        if not prefix:
            prefix = self.input_file.audio_file_name
        if not chunk_size:
            chunk_size = self.chunk_size

        i = self.ms_start
        j = 1
        while i < self.ms_end:
            # split audio to the i-th chunk of chunk_size size.
            # note that if it's the last chunk (first if), maybe it is shorter. 
            if self.ms_start + chunk_size > self.ms_end:
                chunk = self.input_file.audio[self.ms_start:self.ms_end - 1]
            else:
                chunk = self.input_file.audio[self.ms_start:self.ms_start + chunk_size]
            # create associated file (named like: filename_chunk_1.wav)
            # and add it into a list (this files will be delete in the end)
            chunk_file = prefix+ "_chunk_" + str(j) + ".wav"

            # create Chunk istance and add it to a list
            self.chunks.append(Chunk(j - 1, chunk, chunk_file, self.ms_start, self.ms_start + chunk_size))

            # update vars for the while loop
            self.ms_start += chunk_size
            i = self.ms_start
            j += 1

    def start_parsing(self) -> None:
        """ Start parsing.
            It creates a list of threads. Every threads will process a bunch
            of chunks.
        """
        # if threads are not already created
        if len(self.parsing_threads) == 0:
            self.init_threads()

        starter = _Start(self, self.parsing_threads)
        starter.start()
        starter.join()
        self.finish_parse(starter._text, starter.elapsed_time)

    def init_threads(self) -> None:
        """ Create a threads list. Every element is a Thread, and a bunch of
            chunks are given to every thread.
        """

        # if chunks are not already created
        if len(self.chunks) == 0:
            self.create_chunks()
        chunks_num = len(self.chunks)  # number of chunks created

        # if there are more threads than chunks, set threads number to chunks number
        if chunks_num < self.THREADS:
            self.THREADS = chunks_num

        # split in equal part chunks to assing to the threads. 
        # if odd, the last thread will have more chunks.
        split_chunks = [[] for i in range(self.THREADS)]
        for i,c in enumerate(self.chunks):
            split_chunks[i % self.THREADS].append(c)
        # create threads list from the splitted chunks
        for thread_id,chunks in enumerate(split_chunks):
            self.parsing_threads.append(_Parsing(self, chunks, thread_id))
        # this is used to keep the text ordered!
        _Parsing.text = [False] * (chunks_num)

    def finish_parse(self, text, elapsed_time: float=0.0) -> None:
        """ Invoke at the end of parsing. It save the result on file and show it
            on log text box. Furthermore, delete created chunks file and show a pop up
            that inform for the finish.

        Parameters:
            text (str): result
            elapsed_time (float, optional): parsing run time. Defaults 0.0.
        """
        self.output_text = text
        self.elapsed_time = elapsed_time
        # save result on file
        if len(text) > 2:
            with open(self.output_file, "w+") as f:
                self.output_text = self.output_text[0].upper() + self.output_text[1:].lower()
                self.output_text = self.output_text.replace("\n", " ")
                f.write(self.output_text)

        # delete files
        self.delete_chunks()
        # re-init Didi
        self.after_finish()

    def delete_chunks(self) -> None:
        """ Delete chunk files
        """        
        for chunk in self.chunks:
            f = chunk._file_name
            try:
                os.remove(f)
            except:
                continue

    def after_finish(self) -> None:
        """ Re-init Didi after the job is done
        """
        self.init(self.context, self.input_file, self.ms_start, \
            self.ms_end, self.output_file, chunk_size=self.chunk_size, output_text=self.output_text, lan=self.lan, elapsed_time=self.elapsed_time)

    def exit(self) -> None:
        """ Force-stop the job
        """
        self.delete_chunks()
        # stop the threads
        if self.starter:
            self.starter.stop()

# ------------------ Classes used by Didi to perform the parsing --------------

class _Start(Thread):
    """ This class handles the start of the parsing.
        It starts the threads and waits for their end.
    """

    def __init__(self, context: Didi, parsing_threads):
        """ Init

        Parameters:
            parsing_threads (list): list of _Parsing to run
        """
        Thread.__init__(self)
        self.context = context
        self._parsing_threads = parsing_threads

        self._text = "" # in here will be the whole result

        self.stopping = False

    def stop(self):
        """ If force-stopped, stops all the threads and itself
        """
        for t in self._parsing_threads:
            t.stop()
        self.stopping = True

    def run(self):
        """ Run every thread in threads list and waits for their end.
            A timer is started to compute run time.
        """
        start_time = time.time()

        # start parsing thread
        for t in self._parsing_threads:
            t.start()

        for t in self._parsing_threads:
            t.join()

        # at the end, save the result in text
        text = _Parsing.text
        for t in text:
            if t:
                self._text += t + "\n"
        _Parsing.text = []

        self.elapsed_time = time.time() - start_time

        # if force-stopped
        if self.stopping:
            return

class _Parsing(Thread):
    """ This class handles the parse of a list of chunks.
    """

    # in here will be the result of every thread
    TEXT = []

    def __init__(self, context: Didi, chunks: list=[], thread_id: int=0):
        Thread.__init__(self)
        self._r = sr.Recognizer()
        self.context = context
        self._chunks = chunks
        self._id = str(thread_id)

        self._done = 0
        self._text = ""

        self.stopping = False

    def stop(self):
        self.stopping = True

    def run(self):
        """ It parses a bunch of chunks.
            So, for every chunk in chunks, it takes the audio
            and converts it into text.
            In the end of every parse, it appends the current text (text_tmp) to the
            its whole text (self._text).
        """

        for c in self._chunks:
            if self.stopping:
                break
            c._chunk.export(c._file_name, format="wav")
            wav = sr.AudioFile(c._file_name)

            with wav as source:
                self._r.pause_threshold = 3.0
                listen = self._r.listen(source)

            try:
                text_tmp = self._r.recognize_google(listen, language=self.context.lan)
                self.finish_a_chunk(c, text_tmp)
            except Exception as e:
                pass

    def finish_a_chunk(self, chunk, txt) -> None:
        """ In the end of every chunk parse, it append the text
            just parsed to the its whole text (self._text)

        Args:
            chunk ([type]): [description]
            txt ([type]): [description]
        """
        self._text += "\n" + txt
        # this is important to keep the text order!
        _Parsing.text[chunk._number] = txt
        chunk._done = True
        chunk._text = txt
        self._done += 1
        self.context.done_chunks.append(chunk)

    def __str__(self):
        return ("Files: " + str(self._chunks))
