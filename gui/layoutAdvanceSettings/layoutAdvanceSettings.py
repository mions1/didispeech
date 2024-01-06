from typing import Callable

import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
import PyQt6.QtWidgets as qt


class LayoutAdvanceSettings:
    _instance = None
    layout = qt.QGridLayout()
    _e_n_threads: qt.QLineEdit = None
    _e_chunk_size: qt.QLineEdit = None
    _b_select_input_file: qt.QPushButton = None
    _b_select_output_file: qt.QPushButton = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LayoutAdvanceSettings, cls).__new__(cls)
            cls.layout = cls.create_layout_advance_settings()

        return cls._instance

    @classmethod
    def create_layout_advance_settings(cls):
        f_advance_settings = qt.QHBoxLayout()
        cls._e_n_threads = qt.QLineEdit()
        cls._e_n_threads.setPlaceholderText("#Threads: default 8")
        cls._e_chunk_size = qt.QLineEdit()
        cls._e_chunk_size.setPlaceholderText("Chunk size (1000-60000): default 50000")
        e_chunk_size_regex = qtc.QRegularExpression("^[1-5][0-9]{3,4}|60000")
        e_chunk_size_validator = qtg.QRegularExpressionValidator(e_chunk_size_regex, cls._e_chunk_size)
        cls._e_chunk_size.setValidator(e_chunk_size_validator)
        f_advance_settings.addWidget(cls._e_n_threads)
        f_advance_settings.addWidget(cls._e_chunk_size)

        return f_advance_settings

    @classmethod
    def get_e_chunk_size_text(cls):
        return cls._e_chunk_size.text()

    @classmethod
    def get_e_n_threads_text(cls):
        return cls._e_n_threads.text()