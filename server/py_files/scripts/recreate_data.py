#!/usr/bin/env python3
# This script assumes that it will be used in a *nix environment
import os
import subprocess
 # Delete especified file types 
def delete_files(files):
    delete = ''.join(['rm -rf ', files])
    os.system(delete)
    
def delete_data():
    # Delete json resumes
    delete_files('server/data/DB/resumes/*.json')
    
    # Delete txt resumes
    delete_files('server/data/resumes-txt/*.txt')
     # I have not found a proper way to call the GenerateDB.js function from python.
    subprocess.call("node server/GenerateDB.js", shell=True)
 # Delete the data
delete_data() 
