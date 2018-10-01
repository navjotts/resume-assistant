import os
base_resume_name = '/home/antonio/indeed/Indeed_resume_'

for i in range(1000):
    resume = ''.join([base_resume_name, str(i)])
    with open(resume, 'r') as original_file:
        formatted_resume = ''.join([resume, '.txt'])
        with open(formatted_resume, 'w') as new_resume:
            for line in original_file:
                if line.strip() == 'ResumeAI[indeed.com]':
                    new_resume.write(line.replace('ResumeAI[indeed.com]', 'ResumeAI[Source]'))
                elif line.strip() == 'Work Experience':
                    new_resume.write(line.replace('Work Experience', 'ResumeAI[Work Experience]'))
                elif line.strip() == 'Education':
                    new_resume.write(line.replace('Education', 'ResumeAI[Education]'))
                elif line.strip() == 'Skills':
                    new_resume.write(line.replace('Skills', 'ResumeAI[Skills]'))
                elif line.strip() == 'Links':
                    new_resume.write(line.replace('Links', 'ResumeAI[Links]'))
                elif line.strip() == 'Additional Information':
                    new_resume.write(line.replace('Additional Information', 'ResumeAI[Additional Information]'))
                else:
                    new_resume.write(line)
                
