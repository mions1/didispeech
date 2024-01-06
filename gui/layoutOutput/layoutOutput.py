from typing import Callable

import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
import PyQt6.QtWidgets as qt


class LayoutOutput:
    _instance = None
    layout = qt.QVBoxLayout()
    _tb_out: qt.QTextEdit = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LayoutOutput, cls).__new__(cls)
            cls.layout = cls.create_layout_output()

        return cls._instance

    @classmethod
    def create_layout_output(cls):
        f_output = qt.QVBoxLayout()

        # output box (where write log and result)
        cls._tb_out = qt.QTextEdit()
        cls._tb_out.setReadOnly(True)
        tmp_str = "1. Select an audio file\n"
        tmp_str += "2. Set range time to parse\n"
        tmp_str += "3. Press Start button\n"
        tmp_str += "In this box you will see log. Result will be saved on output file"
        cls.tb_insert(tmp_str, True)
        # add it to the layout
        f_output.addWidget(cls._tb_out)

        return f_output

    @classmethod
    def tb_insert(cls, text, replace=False) -> None:
        """ Insert a text into output textbox

        Args:
            text (str): text to write into Textbox
            replace (bool, optional): If true, replace current text,
                otherwise append the new text to it. Defaults to False.
        """
        if replace:
            cls._tb_out.setText(text)
        else:
            cls._tb_out.append(text)

    @classmethod
    def get_tb_out_text(cls) -> str:
        """ Get the current text in output textbox.

        Returns:
            str: text of output textbox
        """
        return cls._tb_out.toPlainText()
