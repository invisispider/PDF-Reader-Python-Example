import os
import re

import pandas as pd
from datetime import datetime

folder = r'C:/Users/attwe/Downloads/Metrc Exports'+'\\'
file_list = os.listdir(folder)
os.chdir('convert')

f_active = []
f_inactive = []
f_clones = []
f_plants = []
f_transfers = []
f_employees = []
f_general = []

for files in file_list:
    if files.endswith('.csv'):
        f_transfers.append(files)
    elif files.endswith('Packages-Active.xlsx'):
        f_active.append(files)
    elif files.endswith('Packages-Inactive.xlsx'):
        f_inactive.append(files)
    elif files.endswith('Active.xlsx'):
        f_clones.append(files)
    elif files.endswith('Employees.xlsx'):
        f_employees.append(files)
    elif files.endswith('.xlsx'):
        f_plants.append(files)
        f_general.append(files)



params = [('Transfers-', f_transfers), ('PackagesActive-', f_active), ('PackagesInactive-', f_inactive), ('Clones-', f_clones), ('Employees-', f_employees), ('Plants-', f_plants)]

# MAIN COMBINER BLOCK (NOW INCLUDES EMPLOYEES WITH LICENSE NAME AT FRONT
now = datetime.now()
for p in params:
    if p[0] == 'Employees-':
        df = pd.DataFrame()
        for file in p[1]:
            rx_res = re.findall(r"(?:000)\d{3}", file)
            license_name = rx_res[0][3:]
            append1 = pd.DataFrame()
            append1 = append1.append(pd.read_excel(os.path.join(folder + file)), ignore_index=True)
            append1['Full Name'] = append1['First Name']+' '+append1['Last Name']
            full_name_column = append1.pop('Full Name')
            append1.insert(loc=0, column="Full Name", value=full_name_column)
            append1["Export License"] = license_name
            export_license_column = append1.pop("Export License")
            append1.insert(loc=0, column="Export License", value=export_license_column)
            df = df.append(append1, ignore_index=True)
        df.to_csv(p[0] + now.strftime("%Y%m%d") + '.csv', index=False)
    if p[0] == 'Transfers-':
        df = pd.DataFrame()
        for file in p[1]:
            rx_res = re.findall(r"(?:000)\d{3}", file)
            license_name = rx_res[0][3:]
            try:
                # add 'Report License' column
                append1 = pd.DataFrame()
                append1 = append1.append(pd.read_csv(os.path.join(folder + file)), ignore_index=True)
                append1["Export License"] = license_name
                df = df.append(pd.read_csv(os.path.join(folder + file)), ignore_index=True)
            except:
                continue
        if len(df) == 0:
            continue
        # duplicates
        df.drop_duplicates()
        # unwanted destination types
        df = df[df['Dest. Facility Type'] != 'AU Grower C']
        df = df[df['Dest. Facility Type'] != 'AU Safety Compliance Facility']
        df = df[df['Dest. Facility Type'] != 'AU Excess Grower']
        df = df[df['Dest. Facility Type'] != 'MMFL Grower C']
        df = df[df['Dest. Facility Type'] != 'MMFL Safety Compliance Facility']
        # returned/rejected
        returns = pd.DataFrame()
        returns = df[df['State'] == 'Returned']
        returns = df[df['State'] == 'Rejected']
        df = df[df['State'] != 'Returned']
        df = df[df['State'] != 'Rejected']
        df.to_csv(p[0]+now.strftime("%Y%m%d")+'.csv', index=False)
        returns.to_csv('Returns-'+now.strftime("%Y%m%d") + '.csv', index=False)
    elif p[0] == 'PackagesActive-':
        df = pd.DataFrame()
        for file in p[1]:
            rx_res = re.findall(r"(?:000)\d{3}", file)
            license_name = rx_res[0][3:]
            append1 = pd.DataFrame()
            append1 = append1.append(pd.read_excel(os.path.join(folder + file)), ignore_index=True)
            append1["Export License"] = license_name
            df = df.append(append1, ignore_index=True)
        df_plantpacks = df[df['Category'] == 'Immature Plants']
        df_plantpacks.to_csv('PlantPacks-'+now.strftime("%Y%m%d")+'.csv', index=False)
        df.to_csv(p[0]+now.strftime("%Y%m%d")+'.csv', index=False)
    else:
        df = pd.DataFrame()
        for file in p[1]:
            rx_res = re.findall(r"(?:000)\d{3}", file)
            license_name = rx_res[0][3:]
            append1 = pd.DataFrame()
            append1 = append1.append(pd.read_excel(os.path.join(folder + file)), ignore_index=True)
            append1["Export License"] = license_name
            df = df.append(append1, ignore_index=True)
        df.to_csv(p[0]+now.strftime("%Y%m%d")+'.csv', index=False)


exit()

# # GENERAL xlxs->csv COMBINING: UNCOMMENT THIS. Might need to comment out end to prevent errors.
# params = [('xlsxCombiner-', f_general)]
# now = datetime.now()
# for p in params:
#     df = pd.DataFrame()
#     for file in p[1]:
#         rx_res = re.findall(r"(?:000)\d{3}", file)
#         license_name = rx_res[0][3:]
#         append1 = pd.DataFrame()
#         append1 = append1.append(pd.read_excel(os.path.join(folder + file)), ignore_index=True)
#         append1["Export License"] = license_name
#         export_license_column = append1.pop("Export License")
#         append1.insert(loc= 0 , column=17, value=export_license_column)
#         df = df.append(append1, ignore_index=True)
#     df.to_csv(p[0] + now.strftime("%Y%m%d") + '.csv', index=False)

