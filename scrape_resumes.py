from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time

# create a new fireforx session
driver = webdriver.Firefox()
driver.implicitly_wait(30)
# Open browser in with this site
driver.get('https://resumes.indeed.com')

# Read the resume links from the text file
resumes_url = ['']
with open('/home/antonio/repos/resume-assistant/resume_links.txt', 'r') as resume_links:
    for link in resume_links:
        resumes_url.append(link)
resumes_url.pop(0)


# Create the resumes
for url in resumes_url:
    
    resume_index = str(resumes_url.index(url))
    resume_name = ''.join(['indeed_resume_', resume_index])

    # Navigate to the resume's location 
    driver.get(url)
    resume_body = driver.find_elements_by_class_name('rezemp-ResumeDisplay-body')

    with open(resume_name, 'w') as write_resume:
        write_resume.write('ResumeAI[indeed.com]\n')
        write_resume.write(url)
        write_resume.write('\n')
        for element in resume_body:
            write_resume.write(element.text)

    # Wait 10 seconds before going to the next resume    
    time.sleep(10)