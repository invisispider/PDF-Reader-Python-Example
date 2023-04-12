import io
from os import listdir
from os.path import isfile, join
import pandas as pd


# FIRST STEP: RUN POWERAUTOMATE SCRIPT TO CONVERT PDFS TO TEXT
# KEEP THEM IN THE SAME INPUT FOLDER WITH THE REGULAR PDFS.


def get_strain(field):
    file_path = "<your_input_folder>"
    with io.open(file_path + 'strains.txt', 'r') as strains:
        for strain in strains:
            field = field.lower()
            if strain.lower().strip() in field:
                return strain.strip()



def percent_handler(string):
    string = string.replace(' ', '')
    index = string.find('%')
    donoin_string = string[0:(index+1)]
    return donoin_string
    # for sub in split_string:
    #     if re.match(".+%", sub):
    #         return sub.strip()




def get_data_viridis(coa):
    r = dict()
    r['Lab Name'] = 'PSI Labs'
    r['Sample Name'] = coa[6].strip()
    r['Strain'] = get_strain(coa[6])

    for line in coa:

        if line.endswith('Fail'):
            r['Pass/fail?'] = 'Failed'

        string = 'Sample ID: '
        if line.startswith(string):
            r['Sample ID'] = line.replace(string, '').strip()

        string = '1A4050'
        if line.startswith(string):
            r['Regulator ID'] = line.strip()

        string = 'Completed: '
        if string in line:
            line = line.replace(string, '').strip()
            r['Date Completed'] = line[-11:].strip()

        string = 'Date Received: '
        if string in line:
            line = line.replace(string, '').strip()
            r['Date Received'] = line[-11:].strip()

        string = 'Matrix: '
        if line.startswith(string):
            r['Category'] = line.replace(string,'').strip()

        string = 'Type: '
        if line.startswith(string):
            r['Type'] = line.replace(string,'').strip()
            if r['Type'] == 'Preroll':
                r['Type'] = 'Flower - Cured'
            if r['Type'] == 'Concentrates & Extracts':
                r['Type'] = 'Extracts'

        # # MICROBIALS
        micros = [('Coliforms ', 'microbials_coliforms'),
                  ('Yeast & Mold ', 'microbials_yeast_and_mold'),
                  ('E. Coli ', 'microbials_ecoli'),
                  ('Salmonella', 'microbials_salmonella'),
                  ('Aspergillus', 'microbials_aspergillus')]

        for micro in micros:
            string = micro[0]
            reference = micro[1]
            if line.startswith(string):
                if 'Not Detected' in line:
                    r[reference] = 0
                elif ' ND ' in line:
                    r[reference] = 0
                else:
                    targ = line.replace(string,'').split(' ')
                    r[reference] = targ[1].replace(',','').strip()


    if not 'Pass/fail?' in r:
        r['Pass/fail?'] = 'Passed'
    return r


file_path = "<your_output_folder>"

all_files = [f for f in listdir(file_path) if isfile(join(file_path, f))]



with open("<path>\\column_heads_list.txt", "r") as headers:
    csv_headers = headers.readline()

# ALL THE COAS IN THE INPUT FOLDER
text_coas = []

for file in all_files:
    if file.endswith('.txt'):
        if file == 'strains.txt':
            continue
        text_coas.append(file)


rows = []
i = 0
for file in text_coas:
    with io.open(file_path + file, "rt", encoding="UTF-16LE") as f:
        i += 1
        text_coa = f.readlines()
        head = get_data_viridis(text_coa)
        rows.append(head)

new_headers = csv_headers.split(',')
results_df = pd.DataFrame.from_dict(rows)


columnar_df = pd.DataFrame(columns=new_headers)
df = columnar_df.append(results_df)
df.to_csv('big_dataframe.csv')
print(str(i)+'coas successfully built to csv')
print(r'Output saved to <your_path>\big_dataframe.csv')
print(r'for some reason, you\'ll have to go into the output sheet and copy values with strain column')
