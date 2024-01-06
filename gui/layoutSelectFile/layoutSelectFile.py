from typing import Callable

import PyQt6.QtWidgets as qt


class LayoutSelectFile:
    _instance = None
    layout = qt.QGridLayout()
    _b_select_input_file: qt.QPushButton = None
    _b_select_output_file: qt.QPushButton = None

    def __new__(cls, input_file_name: str, output_file_name: str, fun_select_input_file: Callable,
                fun_select_output_file: Callable):
        if cls._instance is None:
            cls._instance = super(LayoutSelectFile, cls).__new__(cls)
            cls.layout = cls.create_layout_select_file(input_file_name, output_file_name, fun_select_input_file,
                                                       fun_select_output_file)

        return cls._instance

    @classmethod
    def create_layout_select_file(cls, input_file_name: str, output_file_name: str, fun_select_input_file: Callable,
                                  fun_select_output_file: Callable):
        # select input file (which one to transcribe)
        f_select_file = qt.QGridLayout()
        l_select_input_file = qt.QLabel("Input file:")
        cls._b_select_input_file = qt.QPushButton(input_file_name)

        # select output file (where to save the transcription)
        l_select_output_file = qt.QLabel("Output file: ")
        cls._b_select_output_file = qt.QPushButton(output_file_name)

        # connect buttons to functions
        cls._b_select_input_file.clicked.connect(lambda a: fun_select_input_file())
        cls._b_select_output_file.clicked.connect(lambda a: fun_select_output_file())

        # add them all to the layout
        f_select_file.addWidget(l_select_input_file, 0, 0)
        f_select_file.addWidget(cls._b_select_input_file, 1, 0)
        f_select_file.addWidget(l_select_output_file, 0, 1)
        f_select_file.addWidget(cls._b_select_output_file, 1, 1)
        f_select_file.addWidget(cls.get_QHline(), 3, 0, 3, 2)
        return f_select_file

    @classmethod
    def set_text_b_select_input_file(cls, text: str):
        cls._b_select_input_file.setText(text)

    @classmethod
    def set_text_b_select_output_file(cls, text: str):
        cls._b_select_output_file.setText(text)

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
