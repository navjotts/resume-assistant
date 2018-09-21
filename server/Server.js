const fs = require('fs');
const path = require('path');
const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');

const PythonConnector = require('./PythonConnector.js');
const DocxParser = require('./DocxParser.js');

var storage = multer.diskStorage({
    destination: function (req, file, callback) {
        callback(null, path.join(__dirname, 'uploads'));
    },
    filename: function (req, file, callback) {
        callback(null, file.originalname);
    }
});
var upload = multer({ storage: storage }, { limits: { files: 1 } }).single('userFile');

var app = express();

app.set('views', path.join(__dirname, '..', 'client', 'views'));
app.set('view engine', 'pug');
app.use(express.static(path.join(__dirname, '..', 'client', 'public')));

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use(function (req, res, next) {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Max-Age', 7200);
    res.header('Access-Control-Allow-Headers', 'X-Requested-With');
    res.header('Access-Control-Allow-Headers', 'Content-Type');
    next();
});

app.get('/', function (req, res) {
    console.log(req.url);
    res.render('index', { title: 'Resume Assistant' });
});

app.get('/training', function (req, res) {
    console.log(req.url);
    res.render('dashboard', { title: 'Resume Assistant' });
});

app.get('/training/resumes', function (req, res, next) {
    console.log(req.url);
    var resumes = [];
    var dbDir = path.join(__dirname, 'data', 'DB', 'resumes');
    var files = fs.readdirSync(dbDir).filter(fileName => fileName.split('.').pop() === 'json');
    files.forEach(fileName => resumes.push(fileName.split('.')[0]));
    res.json(resumes);
});

app.get('/training/jobs', function (req, res, next) {
    console.log(req.url);
    var jobs = [];
    var dbDir = path.join(__dirname, 'data', 'DB', 'jobs');
    var files = fs.readdirSync(dbDir).filter(fileName => fileName.split('.').pop() === 'json');
    files.forEach(fileName => jobs.push(fileName.split('.')[0]));
    res.json(jobs);
});

app.get('/training/resumes/:id', function (req, res, next) {
    console.log(req.url);
    var parent = 'resumes';
    var resumeId = req.params.id;
    var dbDir = path.join(__dirname, 'data', 'DB', parent);
    var files = fs.readdirSync(dbDir).filter(fileName => fileName.split('.').pop() === 'json');

    if (resumeId < 0 || resumeId >= files.length) {
        console.log('resumeId doesn\'t exist', resumeId);
        res.send(404);
    }
    else {
        var fileName = files[resumeId];
        var resumeData = JSON.parse(fs.readFileSync(path.join(dbDir, fileName)));
        res.render('document', {
            parentId: parent,
            id: resumeId,
            sents: resumeData.content,
            title: 'Resume#' + resumeId
        });
    }
});

app.get('/training/jobs/:id', function (req, res, next) {
    console.log(req.url);
    var parent = 'jobs';
    var jobId = req.params.id;
    var dbDir = path.join(__dirname, 'data', 'DB', parent);
    var files = fs.readdirSync(dbDir).filter(fileName => fileName.split('.').pop() === 'json');

    if (jobId < 0 || jobId >= files.length) {
        console.log('jobId doesn\'t exist', jobId);
        res.send(404);
    }
    else {
        var fileName = files[jobId];
        var jobData = JSON.parse(fs.readFileSync(path.join(dbDir, fileName)));
        res.render('document', {
            parentId: parent,
            id: jobId,
            sents: jobData.content,
            title: fileName
        });
    }
});


// TODO error handling inside these
app.post('/training/:parent/:docId/sentences/:sentenceId/edit', function (req, res, next) {
    console.log(req.url);
    var parent = req.params.parent;
    var docId = req.params.docId;
    var sentenceId = req.params.sentenceId;
    var label = req.body.label;

    var dbDir = path.join(__dirname, 'data', 'DB', parent);
    var files = fs.readdirSync(dbDir).filter(fileName => fileName.split('.').pop() === 'json');
    var fileName = files[docId];
    var docData = JSON.parse(fs.readFileSync(path.join(dbDir, fileName)));
    docData.content[sentenceId].label = label;
    fs.writeFileSync(path.join(dbDir, fileName), JSON.stringify(docData));
    res.json(docData.content[sentenceId]);
});


// TODO need error handling
app.post('/upload', function (req, res, next) {
    console.log(req.url);
    upload(req, res, function (err) {
        if (err) {
            res.end("Error uploading file");
        }
        else {
            res.end("File upload success");
        }
    });
});

function collectData(parent, name) {
    var samples = [];
    var labels = [];
    var dbDir = path.join(__dirname, 'data', parent, name)
    var files = fs.readdirSync(dbDir);
    for (var i = 0; i < files.length; i++) {
        var fileName = files[i];
        if (fileName.split('.').pop() === 'json') {
            var docData = JSON.parse(fs.readFileSync(path.join(dbDir, fileName)));
            var emptyLabels = docData.content.filter(each => each.label.length==0);
            if (emptyLabels.length == 0) {
                docData.content.forEach(each => {
                    samples.push(each.sentence);
                    labels.push(each.label === 'WORK EXPERIENCE' ? 'EXPERIENCE' : each.label); // TODO https://github.com/navjotts/resume-assistant/issues/5
                });
            }
            else {
                console.log('NOT LABELLED!', fileName);
            }
        }
    }

    return { samples, labels };
}

app.get('/training/:trainOrTest/:dataset/:modelName/:modelType/:featureType', async function (req, res, next) {
    console.log(req.url);
    var modelName = req.params.modelName;
    if (!['resumes', 'jobs'].includes(modelName)) {
        console.log('wip');
        res.send(200);
        return;
    }

    var trainOrTest = req.params.trainOrTest;
    var dataset = req.params.dataset;
    if (trainOrTest == 'train') {
        dataset = 'DB'; // training should always happens on the training dataset (testing can happen either on training or testing dataset)
    }
    var method = trainOrTest == 'train' ? 'train_classifier' : 'test_classifier';
    var modelType = req.params.modelType;
    var featureType = req.params.featureType;
    try {
        var data = collectData(dataset, modelName);
        console.log(`Starting ${trainOrTest}ing for ${modelName}, on dataset ${dataset}, data size of (samples, labels): (${data.samples.length}, ${data.labels.length})`);

        var result = await PythonConnector.invoke(method, modelName, modelType, featureType, data.samples, data.labels);
        console.log(`Finished ${trainOrTest}ing.`);
        res.json(result);
    }
    catch (e) {
        console.log('error in /training', e);
        res.send(404);
    }
});

app.get('/training/summary', async function (req, res, next) {
    console.log(req.url);
    try {
        var scoresFilePath = path.join(__dirname, 'py_files', 'models', 'scores.json');
        var scoresData = JSON.parse(fs.readFileSync(scoresFilePath));
        res.json(scoresData)
    }
    catch (e) {
        console.log('error in /training/summary', e);
        res.send(404);
    }
});

function sampleSet(destFolder, fileName) {
    if (destFolder === 'jobs') {
        if (fileName.includes('google')) {
            return true;
        }

        if (fileName.includes('dice')) {
            return Math.floor((Math.random()*100)+1) === 100 ? true : false;
        }

        return Math.floor((Math.random()*100)+1) === 100 ? true : false;
    }

    return true;
}

// TODO combine with '/training/embeddings/train'
app.get('/training/sentenceembeddings/train', async function (req, res, next) {
    console.log(req.url);
    try {
        var sents = [];

        var srcFolder = 'resumes-txt';
        console.log(`Collecting sentences from ${srcFolder}...`);
        var srcDir = path.join(__dirname, 'data', srcFolder);
        var files = fs.readdirSync(srcDir);

        for (var i = 0; i < files.length; i++) {
            var fileName = files[i];
            if (fileName.split('.').pop() === 'txt') {
                console.log(`#${i} Collecting sentences for: ${fileName}`);
                var sentences = await PythonConnector.invoke('sentences_from_file_lines', path.join(srcDir, fileName), false, false); // TODO need to think on stop, punct
                sents = sents.concat(sentences);
            }
        }
        console.log('total sents', sents.length);

        var srcFolder = 'jobs-txt';
        console.log(`Collecting sentences from ${srcFolder}...`);
        var srcDir = path.join(__dirname, 'data', srcFolder);
        var files = fs.readdirSync(srcDir);

        for (var i = 0; i < files.length; i++) {
            var fileName = files[i];
            if (fileName.split('.').pop() === 'txt') {
                if (!sampleSet('jobs', fileName)) {
                    continue;
                }

                console.log(`#${i} Collecting sentences for: ${fileName}`);
                var sentences = await PythonConnector.invoke('sentences', fs.readFileSync(path.join(srcDir, fileName)).toString(), false, false); // TODO need to think on stop, punct
                sents = sents.concat(sentences);
            }
        }

        console.log('total sents', sents.length);
        console.log(sents[sents.length-1]);
        await PythonConnector.invoke('train_sent_embeddings', 'resumes_jobs', 100, sents);
        res.json(200);
    }
    catch (e) {
        console.log('error in /training/embeddings', e);
        res.send(404);
    }
});

app.get('/training/embeddings/train', async function (req, res, next) {
    console.log(req.url);
    try {
        var sents = [];
        var srcFolder = 'resumes-txt'; // TODO add jobs also
        console.log(`Collecting sentences from ${srcFolder}...`);
        var srcDir = path.join(__dirname, 'data', srcFolder);
        var files = fs.readdirSync(srcDir);

        for (var i = 0; i < files.length; i++) {
            var fileName = files[i];
            if (fileName.split('.').pop() === 'txt') {
                console.log(`#${i} Collecting sentences for: ${fileName}`);
                var sentences = await PythonConnector.invoke('sentences_from_file_lines', path.join(srcDir, fileName), true, true);
                sents = sents.concat(sentences);
            }
        }

        await PythonConnector.invoke('train_embeddings', 'resumes', 100, sents);
        res.json(200);
    }
    catch (e) {
        console.log('error in /training/embeddings', e);
        res.send(404);
    }
});

app.get('/training/embeddings/visualize', async function (req, res, next) {
    console.log(req.url);
    try {
        var embeddingsFilePath = path.join(__dirname, 'py_files', 'models', 'Embeddings', 'trained', 'embeddings2d.csv');
        var coordinates = [] // [{word, xcoord, ycoord}, ...]
        var embeddingsFileContent = fs.readFileSync(embeddingsFilePath).toString().split('\n');
        for (var i = 1; i <= embeddingsFileContent.length; i++) {
            var rowEntry = embeddingsFileContent[i];
            if (rowEntry) {
                var rowDetails = rowEntry.split(',');
                coordinates.push({
                    'word': rowDetails[1],
                    'xcoord': rowDetails[2],
                    'ycoord': rowDetails[3]
                });
            }
        }
        res.json(coordinates);
    }
    catch (e) {
        console.log('error in /training/embeddings', e);
        res.send(404);
    }
});


app.get('/training/embeddings/generatecoordinates/:dimension', async function (req, res, next) {
    console.log(req.url);
    var dimension = req.params.dimension;
    try {
        await PythonConnector.invoke('generate_embeddings_coordinates', 'resumes', 100, Number(dimension));
        res.json(200);
    }
    catch (e) {
        console.log('error in /training/embeddings', e);
        res.send(404);
    }
});

app.get('/analyze/:resumeFile/:jobFile', async function (req, res, next) {
    console.log(req.url);
    var resumeFileName = req.params.resumeFile;
    var resumeFilePath = path.join(__dirname, 'uploads', resumeFileName);
    var jobFileName = req.params.jobFile;
    var jobFilePath = path.join(__dirname, 'uploads', jobFileName);

    try {
        var resumeFile = fs.readFileSync(resumeFilePath);
        var resumeDoc = await DocxParser.parseAsync(resumeFile);
        var text = '';
        resumeDoc.forEach(para => text = text + (text.length ? '\n' : '') + para.text);

        var tempFilePath = path.join(__dirname, 'uploads', resumeFileName.split('.')[0] + '.txt');
        fs.writeFileSync(tempFilePath, text);
        var resumeSentences = await PythonConnector.invoke('sentences_from_file_lines', tempFilePath);

        var resumeSamples = [];
        resumeSentences.forEach(sent => resumeSamples.push(sent)); // TODO use concat
        var resumeLabelsPredicted = await PythonConnector.invoke('classify_sentences', 'resumes', 'FastText', 'None', resumeSamples);
        console.assert(resumeLabelsPredicted.length == resumeSamples.length);

        var jobFile = fs.readFileSync(jobFilePath).toString();
        var jobSentences = await PythonConnector.invoke('sentences', jobFile);

        var jobSamples = [];
        jobSentences.forEach(sent => jobSamples.push(sent)); // TODO use concat
        var jobLabelsPredicted = await PythonConnector.invoke('classify_sentences', 'jobs', 'FastText', 'None', jobSamples);
        console.assert(jobLabelsPredicted.length == jobSamples.length);

        var jobsData = {};
        jobSamples.forEach((sent, index) => {
            var label = jobLabelsPredicted[index][0];
            if (!jobsData[label]) {
                jobsData[label] = [];
            }
            jobsData[label].push(sent);
        });

        var data = [];
        for (var i = 0; i < resumeSamples.length; i++) {
            resumeSent = resumeSamples[i];
            console.log('resumeSent:', resumeSent.join(' '));
            var resumeLabel = resumeLabelsPredicted[i][0];
            var scores = [];

            if (resumeLabel == 'OTHERS') {
                scores = [1.0]
            }
            else {
                var jobSents = jobsData[resumeLabel];
                scores = await PythonConnector.invoke('sentence_similarity', 'resumes_jobs', 100, resumeSent, jobSents);
            }

            console.log('scores', scores);
            console.log('score', Math.max(...scores));
            data.push({
                sentence: resumeSent.join(' '),
                score: Math.round(Math.max(...scores) * 1000) / 10
            });
        }

        res.json(data);
    }
    catch (e) {
        console.log('error in /analyze', e);
        res.send(404);
    }

    // don't keep the uploaded files around (think about it later)
    [resumeFilePath, jobFilePath, tempFilePath].forEach(each => {
        if (fs.existsSync(each)) {
            fs.unlinkSync(each);
        }
    });
});

app.get('*', function (req, res, next) {
    var err = new Error();
    err.status = 404;
    next(err);
});

app.use(function (err, req, res, next) {
    if (err.status !== 404) {
        return next(err);
    }

    res.status(500);
    res.render('error', { error: err });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Started listening on port ${PORT} ...`));