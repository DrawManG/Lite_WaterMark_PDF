import json
import os
import shutil
from typing import Dict, List

import progressbar
from PyPDF4 import PdfFileReader, PdfFileWriter
from PyQt5.QtWidgets import   QMessageBox

def read_json_file(path):
    """Читает JSON в словарь питон"""
    with open(path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data


class WaterMarks:
    """Модель генерации ватермарок"""
    # Выбранная папка с отчетами
    _initial_directory: str = ""
    
    # Папка с отчетами с ватермаркой
    _modified_directory: str = ""

    # Все PDF файлы из self._initial_directory
    _files: List[str] = []

    # Все файлы ватермарок
    #_watermark: str = "pdf_watermark/5.pdf"
    _watermark: Dict = {
        "vertical": "app_data/vertical.pdf",
        "horizontal": "app_data/horizontal1.pdf"
    }

    _watermark_config: Dict = read_json_file("app_data/configs.json")

    def set_initial_directory(self, directory: str) -> None:
        """Назначение начальной директории"""
        if os.path.exists(directory):
            self._initial_directory = directory
            print("initial directory: {}".format(directory))
            self._make_modified_directory()
            self._files = WaterMarks._get_files(self._initial_directory)
            print("{} files were found".format(len(self._files)))

    def get_initial_directory(self) -> str:
        return self._initial_directory

    def _make_modified_directory(self) -> None:
        """Создадние папки с модифицированными отчетами"""
        if self._initial_directory:
            modified_directory = os.path.join(self._initial_directory, r"modified")
            if os.path.exists(modified_directory):
                shutil.rmtree(modified_directory)
            try:
                os.mkdir(modified_directory)
                self._modified_directory = modified_directory
            except OSError:
                print("failed to create a directory of modified reports")

    def process(self) -> bool:
        """Метод обработки директории, ищет все файлы"""
        if self._files:
            with progressbar.ProgressBar(max_value=len(self._files)) as bar:
                for i, file in enumerate(self._files):
                    file_name = os.path.split(file)[-1]
                    WaterMarks.set_watermark(file, os.path.join(self._modified_directory, file_name),
                                             self._watermark_config, self._watermark,len(self._files),i+1)
                    #bar.update(i)
            return True
        else:
            return False



    @staticmethod
    def set_watermark(input_pdf: str, output_pdf: str, _watermark_config: Dict, watermark: Dict,file_from_folder,real_i) -> None:
        """ Вставка Ватермарки
            :param input_pdf: Исходный файл (путь)
            :param output_pdf: Итоговый файл (путь)
            :param watermark: Ватермарка (путь)
            Все три должны быть с форматом .PDF
            :return: None"""

        pdf_reader = PdfFileReader(input_pdf,strict=False)
        print(' Сейчас идёт: ',input_pdf.split('\\')[1],'   Completed:  ',real_i, ' from ',file_from_folder )

        watermark_rotage = []
        watermark_instance1 = PdfFileReader(watermark['vertical'])
        watermark_instance2 = PdfFileReader(watermark['horizontal'])
        
        i = 0
        while i < pdf_reader.getNumPages():
            w, h = pdf_reader.getPage(i).mediaBox[2], pdf_reader.getPage(i).mediaBox[3]
            if h > w:
                watermark_page = watermark_instance1.getPage(0)
            else:
                watermark_page = watermark_instance2.getPage(0)
            watermark_rotage.append(watermark_page)
            i+=1

        pdf_writer = PdfFileWriter()
        print("*** Processed pages in PDF file: ***")
        procces_page = progressbar.ProgressBar(max_value=pdf_reader.getNumPages())
        page_int = 0
        for page in range(pdf_reader.getNumPages()):
            procces_page.update(page_int)
            page = pdf_reader.getPage(page)
            page.mergePage(watermark_rotage[page_int])
            pdf_writer.addPage(page)
            page_int += 1

        with open(output_pdf, 'wb') as out:
            try:
                pdf_writer.write(out)
            except Exception as error:
               print(error)
               
    @staticmethod
    def _get_files(_initial_directory: str) -> List[str]:
        """Метод поиска всех файлов с расширением PDF в каталоге self._initial_directory"""
        file_paths = []
        for dirpath, dirs, files in os.walk(_initial_directory):
            for filename in files:
                if (filename.upper().endswith(".PDF")):
                    file_paths.append(os.path.join(dirpath, filename))

        if len(file_paths) == 0:
            print("Не найдено файфлов в расширением PDF")

        return file_paths

if __name__ == "__main__":
    WM = WaterMarks()
    WM.set_initial_directory("Example")
    WM.process()

