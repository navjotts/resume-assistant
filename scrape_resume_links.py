from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time

# Launch url
# Initial web page link, each page holds 50 resumes, 0-49 page one, 50-99, page2, etc
base_url = 'https://resumes.indeed.com/search?q=software+engineer+web+developer&l=&searchFields=jt%2Cskills&start='

# create a new fireforx session
driver = webdriver.Firefox()
driver.implicitly_wait(30)
driver.get('https://resumes.indeed.com/search?q=software+engineer+web+developer&l=&searchFields=jt%2Cskills')

# To store the resume urls
resume_links = ['']

# For this initial run we will only try with 1000/50 = 20
# A more elegant way would be to user driver.navigate().to(url) after the first page, in order to no open another browser window
for i in range(20):
    # Multiplication by 50 because that is the number of max resumes per page.
    start_with_resume = str(i * 50)
    url = ''.join([base_url, start_with_resume])
    driver.implicitly_wait(30)

    elements = driver.find_elements_by_class_name('rezemp-u-h4')

    for element in elements:
        resume_links.append(element.get_attribute('href'))

# Wait 20 seconds before going to the next page
    time.sleep(20)
    driver.get(url)

# Delete the first item from the resume_links list which is just ''
resume_links.pop(0)

print('There are', len(resume_links), 'links now!')

# Write the resume links to file resume_links.txt
print("Creating resume_links.txt file.")
with open('resume_links.txt', 'w') as f:
    for link in resume_links:
        if link:
            f.write(link)
            f.write("\n")

print("Done creating resume_links.txt file.")