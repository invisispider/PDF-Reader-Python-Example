import os
import time
import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.chrome.service import Service
import pandas as pd
from getpass import getpass
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

my_username = ''
my_password = ''
pref_transfers_date=''

project_dir = os.getcwd()
output_dir = os.path.join(os.getcwd(), 'output')


# note: you may have to go into the selenium automated browser, navigate to about:config, search for browser.download.useDownloadDir, make sure is false, and any other similar.
if 'mylogin.txt' not in os.listdir():
    with open('mylogin.txt','w') as file:
        file.writelines([''])

print('Checking for login info.')
with open('mylogin.txt','r') as file:
    lines = file.readlines()
if len(lines)==2:
    my_username = lines[0].replace('my_username','').replace('=','').strip()
    my_password = lines[1].replace('my_password','').replace('=','').strip()
else:
    print("For first time use, please input your login information (this will be saved to text file mylogin.txt in project folder!")
    my_username = input("Please input your metrc username [birthdaysoc]: ")
    my_password = getpass("Please input your metrc password: ")
    with open('mylogin.txt','a') as file:
        file.writelines(['my_username='+my_username+'\n','my_password='+my_password])
print('Reminder: please delete mylogin.txt file when sharing or storing. It contains your sensitive Metrc account login.')

def to_bool(st):
    if st=='y':
        return True
    else:
        return False
pref_headless = False
pref_plants = pref_packages = pref_transfers = pref_employees = True

# ADD A START DATE
pref_transfers_date = '01/01/2022'

# OPTIONS INPUTS
# pref_headless = to_bool(input('Do you want to scrape headless (or see browser)? [y/N]: '))
# pref_plants = to_bool(input('Are you scraping plants today? [Y/n]: '))
# pref_packages = to_bool(input('Are you scraping packages today? [Y/n]: '))
# pref_transfers = to_bool(input('Are you scraping transfers today? [Y/n]: '))
# pref_employees = to_bool(input('Are you scraping employees today? (Must be admin!) [Y/n]: '))

# if pref_transfers:
#     while len(pref_transfers_date)!=10:
#         pref_transfers_date = input('Please input the desired start date for transfers reports [01/01/2022]: ')

# pref_combine = to_bool(input('Do you want to combine and reformat the export files after download? [Y/n]: '))
# pref_delete = to_bool(input('Do you want to delete the individual reports after they are combined? [y/N]: '))



opts = Options()
opts.binary = FirefoxBinary(r'./firefox') # firefox/firefox.exe copied from system location
s = Service("./geckodriver") # geckodriver copied from system install

# UPDATE WITH FIREFOX PROFILE NAME
opts.set_preference("profile", r'./<MY_FIREFOX_PROFILE>.default') # this way 100% works on my system. Copied my firefox profile into pwd

# firefox_capabilities = DesiredCapabilities.FIREFOX # might not be needed
# firefox_capabilities['marionette'] = True  # might not be needed

opts.set_preference("browser.download.folderList", 2) # 0: desktop, 1: "Downloads" directory, 2: custom directory
opts.set_preference("download.manager.showWhenStarting", False)

# UPDATE WITH YOUR PATH. REMEMBER TO CREATE 'output' FOLDER!
opts.set_preference("browser.download.dir", "<PATH>/metrc_scrape/output") 

# r"./output", os.path.join(os.getcwd(), 'output'),
opts.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv,application/octet-stream")
# opts.set_preference("startup.homepage_welcome_url", "about:blank") # seems to do the opposite.
opts.set_preference("browser.download.useDownloadDir", True); # True saves to 'Downloads', False opens file manager dialogue
opts.set_preference("browser.link.open_newwindow", 3)

if pref_headless:
    opts.add_argument("--headless")
opts.add_argument("start-maximized")

driver = webdriver.Firefox(service=s, options=opts)

vars = {}


def wait_for_window(timeout=2):
    time.sleep(round(timeout / 1000))
    wh_now = driver.window_handles
    wh_then = vars["window_handles"]
    if len(wh_now) > len(wh_then):
        return set(wh_now).difference(set(wh_then)).pop()

date = datetime.date.today().strftime("%Y%m%d")

# THIS IS THE JANKY PART. YOU HAVE TO TEST EACH LICENSE, BECAUSE DUE TO HIDDEN PARAMETERS, THEY HAVE DIFFERENT TYPES OF BEHAVIOR.
# TEST EACH LICENSE AGAINST EACH TYPE. WHEN YOU FIND A WINNING COMBO, HARD CODE IT HERE.
# HEY, LIKE I SAID, IT'S A HACK!

license_list = [ ('EXAMPLE-LICENSE-TYPE-1', 1),
                      ('EXAMPLE-LICENSE-TYPE-2', 2),
                      ('EXAMPLE-LICENSE-TYPE-3', 3),
                      ('EXAMPLE-LICENSE-TYPE-4', 4),
                      ('EXAMPLE-LICENSE-TYPE-5', 5),
                      ('EXAMPLE-LICENSE-TYPE-6', 6) ]

driver.implicitly_wait(100)
driver.maximize_window()

# UPDATE METRC LINKS FOR YOUR STATE
driver.get("https://mi.metrc.com/log-in?ReturnUrl=%2f")
WebDriverWait(driver, 60).until(
    expected_conditions.element_to_be_clickable((
        By.ID, "username"
    ))
).send_keys(my_username)
driver.find_element(By.ID, "password").send_keys(my_password)
driver.find_element(By.ID, "login_button").click()
wait = WebDriverWait(driver, 60)
wait.until(lambda driver: driver.current_url != "https://mi.metrc.com/log-in?ReturnUrl=%2f")

get_codes = False
if 'Metrc-MI-Industry-BackupCodes.txt' not in os.listdir():
    print('You need personal backup code to get through the multi-factor authentication.')
    exit('Please log into metrc, go to your username, and download your own backup codes for the MFA. Place the backupcodes file in this project directory, then rerun.')

with open('Metrc-MI-Industry-BackupCodes.txt', 'r') as file:
    backup_codes = file.readlines()
    if len(backup_codes) == 1:
        get_codes = True
    backup_code = backup_codes[0]

with open('Metrc-MI-Industry-BackupCodes.txt', 'w') as file:
    for index, line in enumerate(backup_codes):
        if index != 0:
            file.writelines(line)

wait.until(
    expected_conditions.element_to_be_clickable((
        By.XPATH, '//*[@id="mfa-code"]'
    ))
).send_keys(backup_code)
time.sleep(2)
# #mfa-code
wait.until(
    expected_conditions.element_to_be_clickable((
        By.XPATH, '//*[@id="body_content"]/div[2]/div/form/div[2]/div/button[1]'
    ))
).click()
time.sleep(2)

if get_codes:
    print('Downloading new backup codes.')
    # UPDATE WITH YOUR FIRST LICENSE NUMBER
    url = 'https://mi.metrc.com/user/profile?licenseNumber=<FIRST_LICENSE_NUMBER'
    driver.get(url)
    wait.until(
        expected_conditions.element_to_be_clickable((
            By.XPATH, '//*[@id="download-backup-codes"]'
        ))
    ).click()
    time.sleep(1)


for lic in license_list:
    print('Scraping license '+lic[0]+'.')
    if pref_plants:
        if lic[1] != 6:
            # Plants
            url = str("https://mi.metrc.com/industry/" + lic[0] + "/plants")
            driver.get(url)

            # Immature
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH,
                    '/html/body/div[3]/div[2]/div[2]/div/div/div[1]/ul/li[1]/span[2]'
                ))
            ).click()

            if lic[1] == 1:
                WebDriverWait(driver, 60).until(
                    expected_conditions.element_to_be_clickable((By.XPATH,
                                                                 "/html/body/div[3]/div[2]/div[2]/div/div/div/div[1]/div/div[1]/div[3]/div[1]/button"))).click()
            else:
                WebDriverWait(driver, 60).until(
                    expected_conditions.element_to_be_clickable((
                        By.XPATH,
                        '//*[@id="plantbatches-grid"]/div[1]/div[4]/div[1]/button'
                    ))
                ).click()

            # Download Immature
            if lic[1] == 1:
                WebDriverWait(driver, 60).until(
                    expected_conditions.element_to_be_clickable((By.XPATH,
                                                                 "/html/body/div[3]/div[2]/div[2]/div/div/div/div[1]/div/div[1]/div[3]/div[1]/ul/li[1]/a"))).click()
            else:
                driver.find_element(By.CSS_SELECTOR,
                                         '#plantbatches-grid > div.k-header.k-grid-toolbar > div.btn-group.pull-right > div:nth-child(1) > ul > li:nth-child(1) > a').click()

            # Vegetative
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.CSS_SELECTOR, "li.k-state-default:nth-child(4)"
                ))
            ).click()

            # Click Printer
            if lic[1] == 1:
                WebDriverWait(driver, 60).until(
                    expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="plantsvegetative-grid"]/div[1]/div[3]/div[1]/button'))).click()
            else:
                WebDriverWait(driver, 60).until(
                    expected_conditions.element_to_be_clickable((
                        By.XPATH, '//*[@id="plantsvegetative-grid"]/div[1]/div[4]/div[1]/button'))
                ).click()

            # Download Vegetative
            WebDriverWait(driver, 100).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH, "//a[contains(.,\'Vegetative.xlsx\')]"))
            ).click()

            # Flowering
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((By.XPATH,
                                                             '//*[@id="plants_tabstrip"]/ul/li[5]'))).click()

            # Click Printer
            if lic[1] == 1:
                WebDriverWait(driver, 60).until(
                    expected_conditions.element_to_be_clickable((
                        By.XPATH, '//*[@id="plantsflowering-grid"]/div[1]/div[3]/div[1]/button'))).click()
            else:
                WebDriverWait(driver, 60).until(
                    expected_conditions.element_to_be_clickable((
                        By.XPATH, '//*[@id="plantsflowering-grid"]/div[1]/div[4]/div[1]/button'))).click()

            # Download Flowering
            if lic[1] in (1, 2, 5):
                WebDriverWait(driver, 100).until(
                    expected_conditions.element_to_be_clickable((
                        By.CSS_SELECTOR,
                        "#plantsflowering-grid > div.k-header.k-grid-toolbar > div.btn-group.pull-right > div.btn-group.open > ul > li:nth-child(1) > a"
                    ))
                ).click()
                time.sleep(5)
            else:
                WebDriverWait(driver, 100).until(
                    expected_conditions.element_to_be_clickable((
                        By.XPATH,
                        '//*[@id="plantsflowering-grid"]/div[1]/div[4]/div[1]/ul/li[1]/a'
                    ))
                ).click()
                time.sleep(5)
    if pref_packages:
        # Packages
        url = "https://mi.metrc.com/industry/" + lic[0] + "/packages/"

        driver.get(url)

        # Packages Active
        if lic[1] in (1, 3, 4):
            t=0
            while(len(driver.find_elements(By.XPATH, "//li/span[2]")) == 0):
                time.sleep(1)
                t+=1
                if(t==40):
                    driver.refresh()

            driver.find_element(By.XPATH, "//li/span[2]").click()
        elif lic[1] in (2, 5, 6):
            t = 0
            while (len(driver.find_elements(By.XPATH, "//li/span[2]")) == 0):
                time.sleep(1)
                t += 1
                if (t == 40):
                    driver.refresh()
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH, '//*[@id="packages_tabstrip"]/ul/li[1]/span[2]'
                ))
            ).click()

        # Printer Button
        if lic[1] in (1, 5):
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH,
                    '//*[@id="active-grid"]/div[1]/div[3]/div[1]/button'))
            ).click()
        elif lic[1] == 2:
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH,
                    '/html/body/div[3]/div[2]/div[2]/div/div/div/div[1]/div/div[1]/div[4]/div[1]/button'
                ))
            ).click()
        elif lic[1] in (3, 4, 6):
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH,
                    '//*[@id="active-grid"]/div[1]/div[4]/div[1]/button'
                ))
            ).click()

        # Download
        if lic[1] in (1, 5):
            driver.find_element(By.XPATH, "//a[contains(.,\'-Packages-Active.xlsx\')]").click()
        elif lic[1] in (3, 4, 6):
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH, "//a[contains(.,\'-Packages-Active.xlsx\')]"
                ))
            ).click()
        elif lic[1] == 2:
            # Download
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH, '//*[@id="active-grid"]/div[1]/div[4]/div[1]/ul/li[1]/a'
                ))
            ).click()

        # Packages Inactive
        WebDriverWait(driver, 60).until(
            expected_conditions.element_to_be_clickable((
                By.CSS_SELECTOR, "li.k-state-default:nth-child(3) > span:nth-child(2)"
            ))
        ).click()

        # Printer Button
        WebDriverWait(driver, 60).until(
            expected_conditions.element_to_be_clickable((
                By.XPATH,
                '/html/body/div[3]/div[2]/div[2]/div/div/div/div[3]/div/div[1]/div[2]/div[1]/button'))
        ).click()

        # Download
        if lic[1] in (1, 2, 5, 6):
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH,
                    '/html/body/div[3]/div[2]/div[2]/div/div/div/div[3]/div/div[1]/div[2]/div[1]/ul/li[1]/a'))
            ).click()
            time.sleep(2)
        elif lic[1] in (3, 4):
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH, '//*[@id="inactive-grid"]/div[1]/div[2]/div[1]/ul/li[1]/a'))
            ).click()
            time.sleep(2.5)


    if pref_employees:
        # WebDriverWait(driver,60).until(expected_conditions.element_to_be_clickable((
        #         By.LINK_TEXT, "Admin"
        #     ))
        # ).click()

        url = str("https://mi.metrc.com/industry/" + lic[0] + "/admin/employees")
        driver.get(url)

        # Click Print Button
        WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH,
                    '// *[ @ id = "employees-grid"] / div[1] / div[3] / div[1] / button'
                ))
            ).click()

        # Click xlsx Button
        WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.PARTIAL_LINK_TEXT, 'Metrc-Michigan-'+lic[0]+'-Employees.xlsx'
                ))
            ).click()

        time.sleep(2)


    if pref_transfers:

        # Reports
        WebDriverWait(driver, 60).until(
            expected_conditions.element_to_be_clickable((
                By.LINK_TEXT, "Reports"
            ))
        ).click()

        # Today Button
        if lic[1] == 6:
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.XPATH, "/html/body/div[3]/div[2]/div[2]/div/form/div[3]/div[5]/div[2]/div[8]/div/button"
                ))
            ).click()
        else:
            WebDriverWait(driver, 60).until(
                expected_conditions.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    '#reports_control_panel > div.ng-scope > div:nth-child(10) > div.control-group > div:nth-child(8) > div > button'
                ))
            ).click()

        # Click Start Date
        if lic[1] == 6:
            driver.find_element(By.XPATH,
                                     '/html/body/div[3]/div[2]/div[2]/div/form/div[3]/div[5]/div[2]/div[7]/div/input').click()
        else:
            driver.find_element(By.CSS_SELECTOR,
                                     ".report-block:nth-child(10) .controls:nth-child(7) .validate\\["
                                     "custom\\[dateFormat\\]\\]").click()

        # Fill Start Date '05/01/2020'
        if lic[1] == 6:
            driver.find_element(
                By.XPATH,
                '/html/body/div[3]/div[2]/div[2]/div/form/div[3]/div[5]/div[2]/div[7]/div/input'
            ).send_keys(prefs_transfers_date)
        else:
            driver.find_element(By.XPATH, "(//input[@type=\'text\'])[34]").send_keys("05/01/2021")

        # Set Window to get it back when the tab opens
        vars["root"] = driver.current_window_handle
        vars["window_handles"] = driver.window_handles


        # Click Download csv
        if lic[1] == 6:
            # Click Download csv
            driver.find_element(By.XPATH,
                                     '//*[@id="reports_control_panel"]/div[3]/div[5]/div[2]/div[9]/button[3]').click()
        else:
            driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div/form/div[3]/div[10]/div[2]/div['
                                               '9]/button[3]').click()

        # switch back
        vars["win9258"] = wait_for_window(15)
        driver.switch_to.window(vars["root"])

        exports = os.listdir(output_dir)
        if 'TransfersReport.csv' in exports:
            os.remove(os.path.join(output_dir, 'TransfersReport.csv'))

        exports = os.listdir(output_dir)


        while 'TransfersReport.csv' not in exports:
            time.sleep(1)
            exports = os.listdir(output_dir)
        time.sleep(2)
        os.rename(os.path.join(output_dir,'TransfersReport.csv'), os.path.join(output_dir,'Transfers-' + lic[0] + '-' + date + '.csv'))
        time.sleep(2)

        exports = os.listdir(output_dir)
        if 'TransfersReport.csv' in exports:
            file_size = os.stat(os.path.join(output_dir,'TransfersReport.csv'))
            if file_size.st_size > 10:
                os.remove(os.path.join(output_dir,'Transfers-' + lic[0] + '-' + date + '.csv'))
                time.sleep(2)
                os.rename(os.path.join(output_dir,'TransfersReport.csv'), os.path.join(output_dir,'Transfers-' + lic[0] + '-' + date + '.csv'))
            else:
                os.remove(os.path.join(output_dir,'TransfersReport.csv'))


print('Closing Selenium firefox.')
driver.quit()

if pref_combine:
    print("Combining the export files.")

    file_list = os.listdir(output_dir)

    f_active = []
    f_inactive = []
    f_clones = []
    f_plants = []
    f_transfers = []
    f_employees = []

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

    if pref_employees and len(f_employees)!=36:
        print('warning: Expecting a count of 36 licenses for employees. Check that there are 36 or the downloads failed.')

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
                append1 = append1.append(pd.read_excel(os.path.join(output_dir + file)), ignore_index=True)
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
                    append1 = append1.append(pd.read_csv(os.path.join(output_dir + file)), ignore_index=True)
                    append1["Export License"] = license_name
                    df = df.append(pd.read_csv(os.path.join(output_dir + file)), ignore_index=True)
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
                append1 = append1.append(pd.read_excel(os.path.join(output_dir + file)), ignore_index=True)
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
                append1 = append1.append(pd.read_excel(os.path.join(output_dir + file)), ignore_index=True)
                append1["Export License"] = license_name
                df = df.append(append1, ignore_index=True)
            df.to_csv(p[0]+now.strftime("%Y%m%d")+'.csv', index=False)

if pref_delete:
    print('Removing exported files.')
    for file in os.listdir(output_dir):
        os.remove(file)

exit('Thank.')
