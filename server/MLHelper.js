const fs = require('fs');
const path = require('path');

const PythonConnector = require('./PythonConnector.js');

async function train(name) {
    var samples = [];
    var labels = [];
    var dbDir = path.join(__dirname, 'data', 'DB', name)
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

    console.log(`Starting training on data size of (samples, labels): (${samples.length}, ${labels.length})`);
    try {
        var modelPath = path.join(__dirname, 'data', 'models', name);
        var result = await PythonConnector.invoke('train_sentence_classifier', name, modelPath, samples, labels);
        console.log(`Training result of ${name}: Precision=${result.precision}, Recall=${result.precision}`);
    }
    catch (e) {
        console.log('Error in train:', e);
    }
}

async function test(name) {
    var samples = [];
    var labels = [];
    var dbDir = path.join(__dirname, 'data', 'testDB', name)
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

    console.log(`Starting testing on data size of (samples, labels): (${samples.length}, ${labels.length})`);
    try {
        var modelPath = path.join(__dirname, 'data', 'models', name);
        await PythonConnector.invoke('test_sentence_classifier', name, modelPath, samples, labels);
    }
    catch (e) {
        console.log('Error in train:', e);
    }
}

async function start() {
    //await train('resumes');
    //await train('jobs');
    await test('resumes');
}

start();