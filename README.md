# Resume Assistant
Tailor your resume to a given job posting. See how your resume stands against a job posting - and locate areas of improvement.<br/><br/>

<img alt="" src="https://www.dropbox.com/s/x33g37oi4q7p7r5/rezume_comparison.png?dl=0">
<img alt="" src="https://www.dropbox.com/s/i8wqw3wbhepjq33/topic_plot.png?dl=0">

# Setup
## Installing nodejs and python environment
* Mac
    * go to [https://nodejs.org/en/](https://nodejs.org/en/) and download the installer and click on - and follow steps
    * install python3 and pip3 (suggested: Homebrew)
* Windows
    * go to [https://nodejs.org/en/](https://nodejs.org/en/) and download the installer and click on - and follow steps
    * install python3 and pip3 (suggested: Anaconda - [https://www.anaconda.com/download/](https://www.anaconda.com/download/))
* Linux (Debian based)
    ```
    $ sudo apt install build-essential nodejs npm libzmq3-dev python3-dev python3-pip
    ```

<br/>

## Install packages/modules
(in the root folder)
```
$ npm install
$ pip3 install -r requirements.txt
```

<br/>

# Running the app
```
$ npm start
```