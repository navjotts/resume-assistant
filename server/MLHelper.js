const fs = require('fs');
const path = require('path');

const PythonConnector = require('./PythonConnector.js');
const DocxParser = require('./DocxParser.js');

function collectData(parent, name) {
    var samples = [];
    var labels = [];
    var dbDir = path.join(__dirname, 'data', parent, name)
    var files = fs.readdirSync(dbDir);
    for (var i = 0; i < files.length; i++) {
        var fileName = files[i];
        if (fileName.split('.').pop() === 'json') {
            var docData = JSON.parse(fs.readFileSync(path.join(dbDir, fileName)));
            docData.content.forEach(each => {
                samples.push(each.sentence.join(' '));
                labels.push(each.label);
            });
        }
    }

    return {samples, labels};
}

async function train(name) {
    var data = collectData('DB', name);
    console.log(`Starting training on data size of (samples, labels): (${data.samples.length}, ${data.labels.length})`);

    try {
        var modelPath = path.join(__dirname, 'data', 'models', name);
        var result = await PythonConnector.invoke('train_sentence_classifier', name, modelPath, data.samples, data.labels);
        console.log(`Training result of ${name}: Precision=${result.precision}, Recall=${result.precision}`);
    }
    catch (e) {
        console.log('Error in train:', e);
    }
}

async function test(name) {
    var data = collectData('testDB', name);
    console.log(`Starting testing on data size of (samples, labels): (${data.samples.length}, ${data.labels.length})`);

    try {
        var modelPath = path.join(__dirname, 'data', 'models', name);
        await PythonConnector.invoke('test_sentence_classifier', name, modelPath, data.samples, data.labels);
    }
    catch (e) {
        console.log('Error in test:', e);
    }
}

async function classifyResume(name) {
    var srcDir = path.join(__dirname, 'data', 'resumes-docx')
    var files = fs.readdirSync(srcDir);
    var randomFileId = Math.floor(Math.random() * files.length);
    var fileName = files[randomFileId];
    console.log('Predicting sentence classification for', fileName);

    try {
        var file = fs.readFileSync(path.join(srcDir, fileName));
        var doc = await DocxParser.parseAsync(file);
        var text = '';
        doc.forEach(para => text = text + (text.length ? '\n' : '') + para.text);

        var tempFilePath = path.join(__dirname, fileName.split('.')[0] + '.txt');
        fs.writeFileSync(tempFilePath, text);
        var sentences = await PythonConnector.invoke('sentences_from_file_lines', tempFilePath);
        var samples = [];
        sentences.forEach(sent => samples.push(sent.join(' ')));

        var modelPath = path.join(__dirname, 'data', 'models', name);
        var labelsPredicted = await PythonConnector.invoke('classify_sentences', name, modelPath, samples);
        console.log(labelsPredicted);
    }
    catch (e) {
        console.log('Error in classifyResume -', fileName, e);
    }

    if (fs.existsSync(tempFilePath)) {
        fs.unlinkSync(tempFilePath);
    }
}

async function start() {
    //await train('resumes');
    //await train('jobs');
    await test('resumes');
    //await classifyResume('resumes')
}

start();