"""
script to create the .netrc and .dodsrc files and .urs_cookies files in the homedir folder
to be used to download IMERG data from NASA's GPM mission
using the Earthdata Login API.
working directory should contain the files or appropriate path to access these files should be set. a copy of .dodsrc when working dir i
is different from homedir folder, should be put in the working folder (accordingly to schemes prerequisite files diagram (see png in the NASA folder) )    
"""

from subprocess import Popen
from getpass import getpass
import platform


urs = 'urs.earthdata.nasa.gov'    # Earthdata URL to call for authentication
prompts = ['Enter NASA Earthdata Login Username \n(or create an account at urs.earthdata.nasa.gov): ',
           'Enter NASA Earthdata Login Password: ']

#homeDir = os.path.expanduser("~") + os.sep
homeDir = '/home/cacquist/'  
with open(homeDir + '.netrc', 'w') as file:
    file.write('machine {} login {} password {}'.format(urs, getpass(prompt=prompts[0]), getpass(prompt=prompts[1])))
    file.close()

print('Saved .netrc to:', homeDir)

# Set appropriate permissions for Linux/macOS
if platform.system() != "Windows":
    Popen('chmod og-rw ~/.netrc', shell=True)
    
    

from subprocess import Popen
import platform
import os

homeDir = os.path.expanduser("~") + os.sep

# Create .urs_cookies and .dodsrc files
with open(homeDir + '.urs_cookies', 'w') as file:
    file.write('')
    file.close()
with open(homeDir + '.dodsrc', 'w') as file:
    file.write('HTTP.COOKIEJAR={}.urs_cookies\n'.format(homeDir))
    file.write('HTTP.NETRC={}.netrc'.format(homeDir))
    file.close()

print('Saved .urs_cookies and .dodsrc to:', homeDir)

