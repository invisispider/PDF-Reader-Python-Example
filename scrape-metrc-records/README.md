### This is a hack to automate the collection of records from the Metrc cannabis regulatory data tracking system using Selenium.

## INSTRUCTIONS

1. Install geckodriver on your machine. It is OS-specific. Tested on version 0.30.0-1
2. Create a project directory called metrc_scrape_<company>
3. unzip into this project folder
#### CREATE ENVIRONMENT
4. All software will run in the environment except for geckodriver, which must be installed on the os, 
5. You must configure the user profile settings to download without cue to the output folder.

6. `python3 venv sel_env`
7. `source sel_env/bin/activate`
8. `pip3 install requirements.txt`
#### DONT FORGET TO PIP FREEZE

#### Geckodriver is always fine. 
9. Installed on system
10. Installed into environment container

#### Firefox (binary) - I seem to remember an issue where I downgraded from 24 to 22.4.
11. Installed on system
12. Installed into environment container

#### Firefox profile
13. Never use local, it's generated within session

#### Metrc
14. As the site changes, the best binary will also change.
