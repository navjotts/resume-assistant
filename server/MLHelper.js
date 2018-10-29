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
                labels.push(each.label === 'WORK EXPERIENCE' ? 'EXPERIENCE' : each.label); // TODO https://github.com/navjotts/resume-assistant/issues/5
            });
        }
    }

    return {samples, labels};
}

async function train(name) {
    var data = collectData('DB', name);
    console.log(`Starting training on data size of (samples, labels): (${data.samples.length}, ${data.labels.length})`);

    try {
        var result = await PythonConnector.invoke('train_sentence_classifier', name, 'LSTM', 'keras-embeddings', data.samples, data.labels);
        console.log(result);
    }
    catch (e) {
        console.log('Error in train:', e);
    }
}

async function test(name) {
    var data = collectData('DB', name);
    console.log(`Starting testing on data size of (samples, labels): (${data.samples.length}, ${data.labels.length})`);

    try {
        var result = await PythonConnector.invoke('test_sentence_classifier', name, 'LogisticRegression', 'sentence-embeddings', data.samples, data.labels);
        console.log(result);
    }
    catch (e) {
        console.log('Error in test:', e);
    }
}

async function start() {
    await train('resumes');
    // await test('resumes');
}

start();