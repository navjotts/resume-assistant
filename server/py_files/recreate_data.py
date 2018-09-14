#! /usr/bin/python3
# This script assumes that it will be used in a *nix environment
import os
import glob
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

def generate_db():
    # I have not found a proper way to call the GenerateDB.js function from python.
    subprocess.call("/usr/bin/node server/GenerateDB.js", shell=True)  # I read that shell=True is not safe.

def concatenate_txt_resumes():
    # This will delete the old all_resumes.txt file and create a new one.
    os.system("find server/data/resumes-txt -type f -name '*.txt' -exec cat {} +  > all_resumes.txt")



# Delete the data
delete_data()
# Generate the .json and .txt resumes
generate_db()
# Concatenate all .txt resumes into a single file
concatenate_txt_resumes()
