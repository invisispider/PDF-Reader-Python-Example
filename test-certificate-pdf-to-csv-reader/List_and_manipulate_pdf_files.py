import pandas as pd
from os import listdir
from os.path import isfile, join
file_path = "C:\\Users\\attwe\\PycharmProjects\\PDFScrape\\coas\\"
only_files = [f for f in listdir(file_path) if isfile(join(file_path, f))]

new_file_names = []
doc_x_names = []

for file in only_files:
    sanitize_file = file.replace("(1)", "").replace("Copy of ", "")
    if "docx" in file:
        doc_x_names.append(sanitize_file)
    else:
        new_file_names.append(sanitize_file)

df = pd.DataFrame(new_file_names)
print(df)