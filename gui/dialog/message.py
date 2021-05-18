import PyQt5.QtWidgets as qt


class MessageDialog(qt.QMessageBox):
	
	# icon for the message dialog
	ICON_NOICON = qt.QMessageBox.NoIcon
	ICON_INFORMATION = qt.QMessageBox.Information
	ICON_CRITICAL = qt.QMessageBox.Critical

	def __init__(self, title: str="Info", subtitle: str="Info", message: str="", icon: qt.QMessageBox.Icon=ICON_NOICON, show: bool=True):
		""" It shows a message dialog with given information

		Args:
			title (str, optional): Title of the message dialog. Defaults to "Info".
			subtitle (str, optional): Subtitle of the message dialog. Defaults to "Info".
			message (str, optional): Message of the message dialog. Defaults to "".
			icon (qt.QMessageBox.Icon, optional): Icon of the message dialog. Defaults to ICON_NOICON.
			show (bool, optional): If True, the dialog will be showed as it is builded. Defaults to True.
		"""
		super().__init__()
		self._title = title
		self._subtitle = subtitle
		self._message = message
		self._icon = icon

		if show:
			self.show()

	def show(self) -> None:
		""" It shows the message dialog
		"""
		self.setIcon(self._icon)
		self.setText(self._subtitle)
		self.setInformativeText(self._message)
		self.setWindowTitle(self._title)
		self.exec_()