import threading, os
import PyQt6.QtWidgets as qt
import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg

import threading
from os import path

import moviepy.editor
from pydub import AudioSegment

from utils import misc

from gui.dialog.select_file import SelectFileDialog
from gui.dialog.message import MessageDialog

from multithread.multithread import CustomQThread, TimerQThread

from files_management.input_file import InputFile

from core.didi import Didi


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

    def __init__(self, didispeech_app, input_file: str = DEFAULT_INPUT_FILE, output_file: str = DEFAULT_OUTPUT_FILE):
        """ Main class, application

        Args:
            didispeech_app (DidispeechApp): main application
            input_file (str): input file name
            output_file (str): output file name
        """
        super().__init__()
        self._didispeech_app = didispeech_app

        self._input_file = InputFile(input_file)
        self._output_file = output_file

        self.didi = Didi(self, output_file=output_file)

        self._timer = TimerQThread(self)

        self._f_options = None

    def init(self) -> None:
        """ Create layout and widgets like buttons, textbox, etc.
        """

        self.create_layout_select_file()
        self.create_layout_options()
        self.create_layout_advance_settings()
        self.create_layout_output()
        self.create_layout_logo()

        # add all layout to the main frame
        self.addLayout(self._f_select_file, 0, 0)
        self.addLayout(self._f_options, 1, 0, 1, 1)
        self.addLayout(self._f_advance_settings, 2, 0, 1, 2)
        self.addLayout(self._f_output, 4, 0, 2, 2)

    def create_layout_logo(self):
        l_title = qt.QLabel()
        pixmap = qtg.QPixmap(self.DEFAULT_LOGO_FILE)
        l_title.setPixmap(pixmap)
        self._f_select_file.addWidget(l_title, 2, 0, 2, 2)

    def create_layout_options(self):
        self._f_options = qt.QGridLayout()
        # set the transcription start point
        self._l_start = qt.QLabel("Start (hh:mm:ss)")
        self._e_start = qt.QLineEdit()
        self._e_start.setMaxLength(8)
        self._e_start.setInputMask("99:99:99")
        self._e_start.setText("00:00:00")
        self._cb_language = qt.QComboBox()
        self._cb_language.addItems(["Italian", "English"])
        # set the transcription end point
        self._l_end = qt.QLabel("End (hh:mm:ss)")
        self._e_end = qt.QLineEdit()
        self._e_end.setMaxLength(8)
        self._e_end.setInputMask("99:99:99")
        self._e_end.setText("00:00:00")
        self._b_ms_end_to_audio_len = qt.QPushButton("Time to audio len", enabled=False, )
        self._b_ms_end_to_audio_len.clicked.connect(self.ms_end_to_audio_len)
        self._b_ms_end_to_audio_len.setEnabled(False)
        # buttons to start/quit
        self._b_start = qt.QPushButton("Start", enabled=False, default=True)
        self._b_quit = qt.QPushButton("Force quit")
        self._b_advance_settings = qt.QPushButton("Hide advance settings")
        self._b_start.clicked.connect(self.start)
        self._b_quit.clicked.connect(self._didispeech_app.exit)
        self._b_advance_settings.clicked.connect(self.toggle_advance_settings)
        # add them all to the layout
        self._f_options.addWidget(self._l_start, 0, 0)
        self._f_options.addWidget(self._e_start, 0, 1)
        self._f_options.addWidget(self._cb_language, 0, 2)
        self._f_options.addWidget(self._l_end, 1, 0)
        self._f_options.addWidget(self._e_end, 1, 1)
        self._f_options.addWidget(self._b_ms_end_to_audio_len, 1, 2)
        self._f_options.addWidget(self._b_start, 2, 0, 1, 2)
        self._f_options.addWidget(self._b_quit, 2, 2, 1, 2)
        self._f_options.addWidget(self.get_QHline(), 3, 0, 1, 3)
        self._f_options.addWidget(self._b_advance_settings, 4, 0, 1, 3)

    def create_layout_output(self):
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

    def create_layout_advance_settings(self):
        self._f_advance_settings = qt.QHBoxLayout()
        self._e_n_threads = qt.QLineEdit()
        self._e_n_threads.setPlaceholderText("#Threads: default 8")
        self._e_chunk_size = qt.QLineEdit()
        self._e_chunk_size.setPlaceholderText("Chunk size (1000-60000): default 50000")
        e_chunk_size_regex = qtc.QRegularExpression("^[1-5][0-9]{3,4}|60000")
        e_chunk_size_validator = qtg.QRegularExpressionValidator(e_chunk_size_regex, self._e_chunk_size)
        self._e_chunk_size.setValidator(e_chunk_size_validator)
        self._f_advance_settings.addWidget(self._e_n_threads)
        self._f_advance_settings.addWidget(self._e_chunk_size)

    def create_layout_select_file(self):
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
        self._f_select_file.addWidget(self._l_select_input_file, 0, 0)
        self._f_select_file.addWidget(self._b_select_input_file, 1, 0)
        self._f_select_file.addWidget(self._l_select_output_file, 0, 1)
        self._f_select_file.addWidget(self._b_select_output_file, 1, 1)
        self._f_select_file.addWidget(self.get_QHline(), 3, 0, 3, 2)

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
        self.didi.input_file = self._input_file
        self._b_select_input_file.setText(path.basename(input_file))
        # load audio in another thread because it can be slow
        qthread_load_audio = CustomQThread(self, "self.didi.load_audio()", didi=self.didi)
        qthread_load_audio.start()
        # call set_audio() as the audio is loaded, so it enables start and sets the end point to audio len
        qthread_load_audio.qthread_finish_signal.connect(lambda: self.set_audio())

        # meanwhile loading audio, print loading
        self._timer.start()
        self._timer.qthread_timer_signal.connect(lambda: self.print_loading())

    def set_audio(self) -> None:
        """ Load the audio into the application, setting the end point of the parsing
            to the audio len and enabling the Start button
        """
        self._timer.stop()
        audio_len = self.didi.input_file.get_audio_len()
        self._e_end.setText(misc.ms_2_time(audio_len))
        self._b_start.setEnabled(True)
        self._b_ms_end_to_audio_len.setEnabled(True)

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
        self.didi.output_file = self._output_file
        self._b_select_output_file.setText(path.basename(output_file))

    def start(self) -> None:
        """ After the users set input_file, output_file, start and end points,
            the parsing is started.
            The parsing will be started in another thread so the gui remains
            responsive.
            After the parse, an information dialog will be showed.
        """
        # get the start and end points
        self._start = self._e_start.text()
        self._end = self._e_end.text()

        ms_start, ms_end = misc.time_2_ms(self._start, self._end)

        # if ms_start == 0 maybe self._start is unset, so adjust it
        if ms_start == 0:
            self._start = "00:00:00"
        # same for ms_end. Further, if ms_end == 0, set ms_end to audio length
        if ms_end == 0:
            self._end = "00:00:00"

        # set values for didi object
        self.didi.ms_start = ms_start
        self.didi.ms_end = ms_end

        # set transcript language
        self.didi.lan = self.getLanguage()

        # get advance settings values (if setted)
        chunk_size = self._e_chunk_size.text()
        if chunk_size.isdigit() and chunk_size > 1:
            self.didi.chunk_size = int(chunk_size)
        n_threads = self._e_n_threads.text()
        if n_threads.isdigit():
            self.didi.THREADS = int(n_threads)

        # start parse in another thread
        qthread_start = CustomQThread(self, "self.didi.start()", didi=self.didi)
        qthread_start.start()
        qthread_start.qthread_finish_signal.connect(lambda: self.finish_parse())
        self._b_start.setEnabled(False)

        # meanwhile parsing, print loading
        self._timer.start()
        self._timer.qthread_timer_signal.connect(lambda: self.print_loading())

    def finish_parse(self) -> None:
        """ Invoke at the end of parsing. It save the result on file and show it
            on log text box. Furthermore, it shows a dialog message
            which informs for the finish.
        """
        self._timer.stop()
        # re-enable button
        self._b_start.setEnabled(True)

        # show result in text box and show a dialog message
        self.tb_insert("------------ RESULT -----\n" + self.didi.output_text, replace=True)
        MessageDialog("Finish", "Parsing done in " + misc.s_2_time(self.didi.elapsed_time), \
                      "Result saved in " + self._output_file, MessageDialog.ICON_INFORMATION)

    def getLanguage(self) -> str:
        """ Return the choosen language in tag form.add()

        Returns:
            str: tag of choosen language
        """
        language = self._cb_language.currentText()

        if language == "Italian":
            return "it-IT"
        if language == "English":
            return "en-EN"

    def ms_end_to_audio_len(self):
        """ Set ms end to audio lenght
        """
        audio_len = self.didi.input_file.get_audio_len()
        self._e_end.setText(misc.ms_2_time(audio_len))

    def toggle_advance_settings(self) -> None:
        """ Toggle visibility of advance settings layout
        """
        is_visible = self._f_advance_settings.itemAt(0).isEmpty()

        new_text = "Hide advance settings" if is_visible \
            else "Show advance settings"
        self._b_advance_settings.setText(new_text)

        for i in range(self._f_advance_settings.count()):
            self._f_advance_settings.itemAt(i).widget().setHidden(not is_visible)

    def print_loading(self) -> None:
        """ Print loading text
        """
        if not self._timer.stopped:
            current_text_list = self.tb_get_text().split("\n")
            if "Loading" in current_text_list[-1]:
                current_text_list[-1] = current_text_list[-1] + "."
            else:
                current_text_list.append("Loading.")
            self.tb_insert("\n".join(current_text_list), replace=True)
        else:
            self.tb_insert("Done!", replace=False)

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
        qhline.setFrameShape(qhline.Shape.HLine)
        qhline.setFrameShadow(qhline.Shadow.Plain)
        return qhline
