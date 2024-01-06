from typing import Callable

import PyQt6.QtWidgets as qt


class LayoutOptions:
    _instance = None
    layout = qt.QGridLayout()
    _e_start: qt.QLineEdit = None
    _e_end: qt.QLineEdit = None
    _cb_language: qt.QComboBox = None
    _b_ms_end_to_audio_len: qt.QPushButton = None
    _b_start: qt.QPushButton = None
    _b_quit: qt.QPushButton = None
    _b_advance_settings: qt.QPushButton = None

    def __new__(cls, fun_start: Callable,
                fun_ms_end_to_audio_len: Callable, fun_advance_settings: Callable, fun_quit: Callable):
        if cls._instance is None:
            cls._instance = super(LayoutOptions, cls).__new__(cls)
            cls.layout = cls.create_layout_options(fun_start, fun_ms_end_to_audio_len, fun_advance_settings, fun_quit)

        return cls._instance

    @classmethod
    def create_layout_options(cls, fun_start: Callable, fun_ms_end_to_audio_len: Callable,
                              fun_advance_settings: Callable, fun_quit: Callable):
        f_options = qt.QGridLayout()

        # set the transcription start point
        l_start = qt.QLabel("Start (hh:mm:ss)")
        cls._e_start = qt.QLineEdit()
        cls._e_start.setMaxLength(8)
        cls._e_start.setInputMask("99:99:99")
        cls._e_start.setText("00:00:00")
        cls._cb_language = qt.QComboBox()
        cls._cb_language.addItems(["Italian", "English"])

        # set the transcription end point
        l_end = qt.QLabel("End (hh:mm:ss)")
        cls._e_end = qt.QLineEdit()
        cls._e_end.setMaxLength(8)
        cls._e_end.setInputMask("99:99:99")
        cls._e_end.setText("00:00:00")
        cls._b_ms_end_to_audio_len = qt.QPushButton("Time to audio len", enabled=False)
        cls._b_ms_end_to_audio_len.clicked.connect(lambda a: fun_ms_end_to_audio_len())
        cls._b_ms_end_to_audio_len.setEnabled(False)

        # buttons to start/quit
        cls._b_start = qt.QPushButton("Start", enabled=False, default=True)
        cls._b_quit = qt.QPushButton("Force quit")
        cls._b_advance_settings = qt.QPushButton("Hide advance settings")
        cls._b_start.clicked.connect(lambda a: fun_start())
        cls._b_quit.clicked.connect(lambda a: fun_quit())
        cls._b_advance_settings.clicked.connect(lambda a: fun_advance_settings())

        # add them all to the layout
        f_options.addWidget(l_start, 0, 0)
        f_options.addWidget(cls._e_start, 0, 1)
        f_options.addWidget(cls._cb_language, 0, 2)
        f_options.addWidget(l_end, 1, 0)
        f_options.addWidget(cls._e_end, 1, 1)
        f_options.addWidget(cls._b_ms_end_to_audio_len, 1, 2)
        f_options.addWidget(cls._b_start, 2, 0, 1, 2)
        f_options.addWidget(cls._b_quit, 2, 2, 1, 2)
        f_options.addWidget(LayoutOptions.get_QHline(), 3, 0, 1, 3)
        f_options.addWidget(cls._b_advance_settings, 4, 0, 1, 3)
        
        return f_options

    @classmethod
    def set_text_b_advance_settings(cls, text: str):
        cls._b_advance_settings.setText(text)

    @classmethod
    def set_text_e_end(cls, text: str):
        cls._e_end.setText(text)

    @classmethod
    def set_enable_b_start(cls, enable: bool):
        cls._b_start.setEnabled(enable)

    @classmethod
    def set_enable_b_ms_end_to_audio_len(cls, enable: bool):
        cls._b_ms_end_to_audio_len.setEnabled(enable)

    @classmethod
    def get_e_start_text(cls):
        return cls._e_start.text()

    @classmethod
    def get_e_end_text(cls):
        return cls._e_end.text()

    @classmethod
    def get_current_text_cb_language(cls):
        return cls._cb_language.currentText()

    @staticmethod
    def get_QHline() -> qt.QFrame:
        """ Return a horizontal line, aestetich purpouse.Q

        Returns:
            qt.QFrame: a horizontal line
        """
        qhline = qt.QFrame()
        qhline.setFrameShape(qhline.Shape.HLine)
        qhline.setFrameShadow(qhline.Shadow.Plain)
        return qhline
