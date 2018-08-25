# Approach
Both a resume and a job description can be treated as a structured document consisting of a given number of parts, let's say:<br/>
* Education
* Work Experience
* Skills/Projects
* Others

The problem statement then, can be broken down into 2 parts:<br/>
1. ML model to pull out the above parts from both the given resume and the job description
2. Another ML model to determine the match of each of the parts

<br/><br/>

# Part1

## Step1: Framework & Labelled Data

We need labelled data for Part1 (supervised approach).

Once we collect the resume and job description data, we need a framework to label the data – and need to construct it such that the underlying structure can be used to automate testing also (cross validation & generalization).

* We can start with parsing resumes and job descriptions as a list of sentences (with each sentence being a list of words)
* Each sentence will be labelled as 1 of the parts decided in the Approach section
* We can create a quick web app where we'll start with a list of resumes and job descriptions, clicking on each gives a list of sentences, with each sentence mapped to a editable TextField with label

Once the above is in place, we can start experimenting with classification models based on word/sentence embeddings.


## Step2: Classification

**Problem Statement:** given a resume (or a job description), classify each sentence into 1 of the categories mentioned in the Approach section

**Things to try**:<br>

Features:
1. Bag of Words / tf-idf
2. Word Embeddings
3. Sentence Embeddings ([https://arxiv.org/pdf/1405.4053.pdf](https://arxiv.org/pdf/1405.4053.pdf))
4. tf-idf on Word Embeddings / weighted embeddings ([https://stackoverflow.com/questions/47727078/what-does-a-weighted-word-embedding-mean](https://stackoverflow.com/questions/47727078/what-does-a-weighted-word-embedding-mean))
5. TF Hub ([https://medium.com/tensorflow/building-a-text-classification-model-with-tensorflow-hub-and-estimators-3169e7aa568](https://medium.com/tensorflow/building-a-text-classification-model-with-tensorflow-hub-and-estimators-3169e7aa568))

Models:
1. Multinomial Logistic Regression
2. SVM
3. LSTM
4. CNN
5. FastText

<br/>

# Part2

**Problem Statement:** given a 2 sets of sentences – let's say SetA for resume and SetB for job description – point out which sentences of SetB don't have any good match in SetA (which implies some part of job description is not being satisfied)

(If the above subset is successfully found, then for the end resume user, we can highlight the closest match of that subset in SetA to point the user which areas of the resume needs improvement)

**Things to try**:<br>
1. Features: same as Part1, word/sentence embeddings
2. Similarity measure using above features (**special mention:** check Universal Sentence Encoder from TFHub)
3. Recursively go 1 level deeper (once you have 'Work Experience', pull out what exact company and number of years)