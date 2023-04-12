from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

import os
from os import listdir
from os.path import isfile, join

file_path = "<PATH>\\coas\\"
only_files = [f for f in listdir(file_path) if isfile(join(file_path, f))]

new_file_names = []

for file in only_files:
    output_string = StringIO()
    with open(file_path + file, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    sample_name = output_string.getvalue().split("Sample No.:")[1].split("Sample Matrix:")[0].replace("\n", "")
    os.rename(file_path + file, file_path + 'dummy\\' + sample_name + '.pdf')
