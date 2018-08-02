# resume-assistant
Given a resume and a job description, highlights parts of the resume which are not a good match.<br/><br/>

## Approach
Both a resume and a job description can be treated as a structured document consisting of a given number of parts, let's say:<br/>
* Education
* Work Experience
* Expertise
* Others

The problem statement then, can be broken down into 2 steps:<br/>
1. ML model to pull out the above parts from both the given resume and the job description
2. Another ML model to determine the match of each of the parts


## Step1
We need labelled data for Step1, once we collect the required data, we need a framework to label the data – and need to construct it such that the underlying structure can be used to automate testing also (cross validation & generalization)

* We can start with parsing resumes and job descriptions as a list of sentences (we might need to go more granular later on)
* Each sentence will be labelled as 1 of the parts decided in the Approach section
* We can create a quick web app where we'll start with a list of resumes and job descriptions, clicking on each gives a list of sentences, with each sentence mapped to a editable TextField with label

Once the above is in place, we can start experimenting with classification models based on word/sentence embeddings.