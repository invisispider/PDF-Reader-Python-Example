import io
from os import listdir
from os.path import isfile, join
import pandas as pd
import re

import sys

# RUN COA_RENAMER FIRST IF THEY HAVEN'T BEEN NAMED THEIR SAMPLE ID

# FIRST STEP: RUN SCRIPT TO CONVERT PDFS TO TEXT
# KEEP THEM IN THE SAME FOLDER WITH THE REGULAR PDFS.


def get_strain(field):
    file_path = "<your_input_folder>"
    with io.open(file_path + 'strains.txt', 'r') as strains:
        for strain in strains:
            field = field.lower()
            if strain.lower().strip() in field:
                return strain



def percent_handler(string):
    split_string = string.split(' ')
    for sub in split_string:
        if re.match(".+%", sub):
            return sub.strip()

def get_data_viridis(coa):
    r = dict()
    batch_id = False
    r['Lab Name'] = 'Viridis Labs'
    for line in coa:

        # HEAD ITEMS
        string = 'Certificate of Analysis for Sample No. '
        if string in line:
            r['Sample ID'] = line.replace(string, '').strip()
        string = 'Customer Unique ID: '
        if string in line:
            r['Sample Name'] = line.replace(string, '').strip()
            strain = get_strain(line)
            r['Strain'] = strain
        string = 'Date Sample Collected/Received: '
        if string in line:
            r['Date Received'] = line.replace(string, '').strip()
        string = 'Report Date: '
        if string in line:
            r['Date Completed'] = line.replace(string, '').strip()
        string = 'Sample Matrix: '
        if string in line:
            viridis_type = line.replace(string, '').strip()
            if viridis_type == 'Bud/ Flower':
                r['Category'] = 'Plant'
                r['Type'] = 'Flower - Cured'
            elif viridis_type in ('Kief(Plant)', 'Kief(Concentrate)', 'Kief'):
                r['Category'] = 'Plant'
                r['Type'] = 'Kief'
            elif viridis_type == 'Cannabis Plant Material':
                r['Category'] = 'Plant'
                r['Type'] = 'Trim'
            elif viridis_type == 'Vape Cartridge':
                r['Category'] = 'Extracts'
                r['Type'] = 'Vape Cart'
            elif viridis_type == 'Other Matrix':
                r['Category'] = 'Other'
                r['Type'] = 'NA'
            else:
                r['Category'] = 'Extracts'
                r['Type'] = 'Other'

        string = 'Overall Result: '
        if string in line:
            string2 = 'PASS'
            if string2 in line:
                r['Pass/fail?'] = 'Passed'
            else:
                r['Pass/fail?'] = 'Failed'
        string = 'Sample METRC ID: '
        if string in line:
            r['Regulator ID'] = line.replace(string, '').strip()
        if line.startswith('1A4050') and not batch_id:
            r['Regulator Batch ID'] = ''+line[0:24].strip()+''
            batch_id = True

        # CANNABINOIDS
        string = 'Tetrahydrocannabinolic Acid (THCA) '
        if string in line:
            r['cannabinoids_thca'] = percent_handler(line)
        string = 'Cannabidiolic Acid (CBDA) '
        if string in line:
            r['cannabinoids_cbda'] = percent_handler(line)
        string = 'Cannabidiol (CBD) '
        if string in line:
            r['cannabinoids_cbd'] = percent_handler(line)
        string = 'Cannabinol (CBN) '
        if string in line:
            r['cannabinoids_cbn'] = percent_handler(line)
        string = 'Delta 9-Tetrahydrocannabinol (THC) '
        if string in line:
            r['cannabinoids_d9_thc'] = percent_handler(line)

        # TERPENES
        string = '(-)-Isopulegol '
        if line.startswith(string):
            r['terpenes_isopulegol'] = percent_handler(line)
        string = '3-Carene '
        if line.startswith(string):
            r['terpenes_3_carene'] = percent_handler(line)
        string = 'a-Pinene '
        if line.startswith(string):
            r['terpenes_alpha_pinene'] = percent_handler(line)
        string = 'Caryophyllene '
        if line.startswith(string):
            r['terpenes_beta_caryophyllene'] = percent_handler(line)
        string = 'D-Limonene '
        if line.startswith(string):
            r['terpenes_delta_limonene'] = percent_handler(line)
        string = 'Eucalyptol '
        if line.startswith(string):
            r['terpenes_eucalyptol'] = percent_handler(line)
        string = 'Geraniol '
        if line.startswith(string):
            r['terpenes_geraniol'] = percent_handler(line)
        string = 'Humulene '
        if line.startswith(string):
            r['terpenes_alpha_humulene'] = percent_handler(line)
        string = 'Linalool '
        if line.startswith(string):
            r['terpenes_linalool'] = percent_handler(line)
        string = 'cis-Ocimene '
        if line.startswith(string):
            r['terpenes_ocimene'] = percent_handler(line)
        string = 'Ocimene '
        if line.startswith(string):
            r['terpenes_beta_ocimene'] = percent_handler(line)
        string = 'p-Cymene '
        if line.startswith(string):
            r['terpenes_ro_cymene'] = percent_handler(line)
        string = 'ß-Myrcene '
        if line.startswith(string):
            r['terpenes_beta_myrcene'] = percent_handler(line)
        string = 'ß-Pinene '
        if line.startswith(string):
            r['terpenes_beta_pinene'] = percent_handler(line)
        string = 'Terpinolene '
        if line.startswith(string):
            r['terpenes_terpinolene'] = percent_handler(line)

        # MICROBIALS AND HEAVY METALS
        string = 'Total Yeast & Mold '
        if line.startswith(string):
            split_list = line.replace(string, '')
            r['microbials_yeast_and_mold'] = split_list.split(' ')[1]
        string = 'Total Coliform Bacteria '
        if line.startswith(string):
            split_list = line.replace(string, '')
            r['microbials_coliforms'] = split_list.split(' ')[1]
        string = 'Moisture Content TESTED '
        if line.startswith(string):
            split_list = line.replace(string, '')
            r['moisture_percent_moisture'] = split_list.split(' ')[0]
        if line.startswith('Water activity PASS ') or line.startswith('Water activity FAIL '):
            split_list = line.split(' ')[3]
            r['water_activity_water_activity'] = split_list
        if line.startswith('Arsenic'):
            split_list = line.replace(string, '')
            r['metals_arsenic'] = split_list.split(' ')[2]
        if line.startswith('Cadmium'):
            split_list = line.replace(string, '')
            r['metals_cadmium'] = split_list.split(' ')[2]
        if line.startswith('Mercury'):
            split_list = line.replace(string, '')
            r['metals_mercury'] = split_list.split(' ')[2]
        if line.startswith('Lead'):
            split_list = line.replace(string, '')
            r['metals_lead'] = split_list.split(' ')[2]
        if line.startswith('Chromium'):
            split_list = line.replace(string, '')
            r['metals_chromium'] = split_list.split(' ')[2]
        if line.startswith('Nickel'):
            split_list = line.replace(string, '')
            if len(split_list.split(' ')) > 2:
                r['metals_nickel'] = split_list.split(' ')[2]
        if line.startswith('Copper'):
            split_list = line.replace(string, '')
            r['metals_copper'] = split_list.split(' ')[2]

        # TOTAL CANNABINOIDS AND TERPS
        if line.startswith('Total Terpenes ') and not line.startswith('Total Terpenes = '):
            # print(line)
            r['terpenes_total'] = percent_handler(line.replace('Total Terpenes ',''))
            # print(percent_handler(line.replace('Total Terpenes ','')))

        if line.startswith('Total Cannabinoids ') and not line.startswith('Total Cannabinoids = '):
            r['cannabinoids_total'] = percent_handler(line.replace('Total Terpenes ',''))


    return r


file_path = "<your_input_folder>"

all_files = [f for f in listdir(file_path) if isfile(join(file_path, f))]



with open("<path>/column_heads_list.txt", "r") as headers:
    csv_headers = headers.readline()

# ALL THE COAS IN THE 'DUMMY' FOLDER
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
print(r'Output saved to <output_path>\big_dataframe.csv')
print(r'for some reason, you\'ll have to go into the output sheet and copy values with strain column')
