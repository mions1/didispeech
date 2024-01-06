import PyQt6.QtWidgets as qt
import PyQt6.QtGui as qtg

from os import path

from gui.layoutOutput.layoutOutput import LayoutOutput
from gui.layoutSelectFile.layoutSelectFile import LayoutSelectFile
from gui.layoutOptions.layoutOptions import LayoutOptions
from gui.layoutAdvanceSettings.layoutAdvanceSettings import LayoutAdvanceSettings
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

        self._layout_select_file: LayoutSelectFile = None
        self._layout_options: LayoutOptions = None
        self._layout_advance_settings: LayoutAdvanceSettings = None
        self._layout_output: LayoutOutput = None

    def init(self) -> None:
        """ Create layout and widgets like buttons, textbox, etc.
        """

        self._layout_select_file = LayoutSelectFile(self._input_file.file_name, self._output_file,
                                                    self.select_input_file, self.select_output_file)
        self._layout_options = LayoutOptions(self.start, self.ms_end_to_audio_len, self.toggle_advance_settings,
                                             self._didispeech_app.exit)
        self._layout_advance_settings = LayoutAdvanceSettings()
        self._layout_output = LayoutOutput()
        self.create_layout_logo()

        # add all layout to the main frame
        self.addLayout(self._layout_select_file.layout, 0, 0)
        self.addLayout(self._layout_options.layout, 1, 0, 1, 1)
        self.addLayout(self._layout_advance_settings.layout, 2, 0, 1, 2)
        self.addLayout(self._layout_output.layout, 4, 0, 2, 2)

    def create_layout_logo(self):
        l_title = qt.QLabel()
        pixmap = qtg.QPixmap(self.DEFAULT_LOGO_FILE)
        l_title.setPixmap(pixmap)
        #self._f_select_file.addWidget(l_title, 2, 0, 2, 2)

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
        self._layout_select_file.set_text_b_select_input_file(path.basename(input_file))
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
        self._layout_options.set_text_e_end(misc.ms_2_time(audio_len))
        self._layout_options.set_enable_b_start(True)
        self._layout_options.set_enable_b_ms_end_to_audio_len(True)

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
        self._start = self._layout_options.get_e_start_text()
        self._end = self._layout_options.get_e_end_text()

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
        chunk_size = self._layout_advance_settings.get_e_chunk_size_text()
        if chunk_size.isdigit() and chunk_size > 1:
            self.didi.chunk_size = int(chunk_size)
        n_threads = self._layout_advance_settings.get_e_n_threads_text()
        if n_threads.isdigit():
            self.didi.THREADS = int(n_threads)

        # start parse in another thread
        qthread_start = CustomQThread(self, "self.didi.start()", didi=self.didi)
        qthread_start.start()
        qthread_start.qthread_finish_signal.connect(lambda: self.finish_parse())
        self._layout_options.set_enable_b_start(False)

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
        self._layout_options.set_enable_b_start(True)

        # show result in text box and show a dialog message
        self._layout_output.tb_insert("------------ RESULT -----\n" + self.didi.output_text, replace=True)
        MessageDialog("Finish", "Parsing done in " + misc.s_2_time(self.didi.elapsed_time), \
                      "Result saved in " + self._output_file, MessageDialog.ICON_INFORMATION)

    def getLanguage(self) -> str:
        """ Return the choosen language in tag form.add()

        Returns:
            str: tag of choosen language
        """
        language = self._layout_options.get_current_text_cb_language()

        if language == "Italian":
            return "it-IT"
        if language == "English":
            return "en-EN"

    def ms_end_to_audio_len(self):
        """ Set ms end to audio lenght
        """
        audio_len = self.didi.input_file.get_audio_len()
        self._layout_options.set_text_e_end(misc.ms_2_time(audio_len))

    def toggle_advance_settings(self) -> None:
        """ Toggle visibility of advance settings layout
        """
        is_visible = self._layout_advance_settings.layout.itemAt(0).isEmpty()

        new_text = "Hide advance settings" if is_visible \
            else "Show advance settings"
        self._layout_options.set_text_b_advance_settings(new_text)

        for i in range(self._layout_advance_settings.layout.count()):
            self._layout_advance_settings.layout.itemAt(i).widget().setHidden(not is_visible)

    def print_loading(self) -> None:
        """ Print loading text
        """
        if not self._timer.stopped:
            current_text_list = self._layout_output.get_tb_out_text().split("\n")
            if "Loading" in current_text_list[-1]:
                current_text_list[-1] = current_text_list[-1] + "."
            else:
                current_text_list.append("Loading.")
            self._layout_output.tb_insert("\n".join(current_text_list), replace=True)
        else:
            self._layout_output.tb_insert("Done!", replace=False)