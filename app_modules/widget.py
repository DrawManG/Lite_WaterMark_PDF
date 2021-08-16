from PyQt5.QtWidgets import  QFileDialog, QMessageBox,  QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal as Signal
import sys
import os

from app_modules.model import WaterMarks

class OutputLogger(QObject):
    emit_write = Signal(str, int)

    class Severity:
        DEBUG = 0
        ERROR = 1

    def __init__(self, io_stream, severity):
        super().__init__()

        self.io_stream = io_stream
        self.severity = severity

    def write(self, text):
        self.io_stream.write(text)
        self.emit_write.emit(text, self.severity)

    def flush(self):
        self.io_stream.flush()

OUTPUT_LOGGER_STDOUT = OutputLogger(sys.stdout, OutputLogger.Severity.DEBUG)
OUTPUT_LOGGER_STDERR = OutputLogger(sys.stderr, OutputLogger.Severity.ERROR)

sys.stdout = OUTPUT_LOGGER_STDOUT
sys.stderr = OUTPUT_LOGGER_STDERR

class WaterMartWidget(QMainWindow, WaterMarks):
    def __init__(self):
        super().__init__()
        uic.loadUi('app_data/MainWindowUi.ui', self)
        self.show()
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.openButton.clicked.connect(self._open_dir)
        self.processButton.clicked.connect(self._process)

        OUTPUT_LOGGER_STDOUT.emit_write.connect(self.append_log)
        OUTPUT_LOGGER_STDERR.emit_write.connect(self.append_log)

    def append_log(self, text, severity):
        text = repr(text)

        if severity == OutputLogger.Severity.ERROR:
            text = '<b>{}</b>'.format(text)

        self.textEdit.append(text)


    def _open_dir(self):
        try:
            directory = QFileDialog.getExistingDirectory(self, 'Select Folder')
            if directory:
                self.set_initial_directory(directory)
            self._format_TextEdit()
        except PermissionError:
            QMessageBox.critical(self, "Ошибка", "Закройте открытые отчеты из папки modified", QMessageBox.Ok)

    def _format_TextEdit(self):
        #text = list(filter(lambda x: x != '\\n', self.text_edit.toPlainText().replace("'", "").split("\n")))
        #s = ""
        #for i in text:
            #s += i + "\n"
        text = self.textEdit.toPlainText().replace('\\n', "").replace("'", "")
        self.textEdit.clear()
        self.textEdit.setText(text)

    def _process(self):
        proc = self.process()
        if proc:
            print("modification completed")
            self._format_TextEdit()
            QMessageBox.about(self, "Сообщение", "Успешно сохранено")
            os.startfile(os.path.realpath(self.get_initial_directory()))
