const fs = require('fs');
const path = require('path');

const PythonConnector = require('./PythonConnector.js');

async function generateDB(srcFolder, destFolder, method) {
    var dbDir = path.join(__dirname, 'data', 'DB', destFolder);
    if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir);
    }

    var srcDir = path.join(__dirname, 'data', srcFolder);
    var files = fs.readdirSync(srcDir);
    for (var i = 0; i < files.length; i++) {
        var fileName = files[i];
        var fileNameSplit = fileName.split('.');
        if (fileNameSplit.pop() === 'txt') {
            if (!sampleSet(destFolder, fileName)) {
                continue;
            }

            console.log(`#${i} Persisting data for: ${fileName} in: ${destFolder}`);

            var destFilePath = path.join(dbDir, fileNameSplit[0] + '.json');
            if (fs.existsSync(destFilePath)) {
                console.log('Already exists in DB');
            }
            else {
                try {
                    var sentences = [];
                    if (method === 'sentences_from_file_lines') {
                        sentences = await PythonConnector.invoke(method, path.join(srcDir, fileName));
                    }
                    else if (method === 'sentences') {
                        sentences = await PythonConnector.invoke(method, fs.readFileSync(path.join(srcDir, fileName)).toString());
                    }

                    var content = [];
                    sentences.forEach((sent) => content.push({sentence: sent, label: ''}));
                    fs.writeFileSync(destFilePath, JSON.stringify({source: fileName, content: content}));
                }
                catch (e) {
                    console.log('Error in parsing:', fileName, e);
                }
            }
        }
    }
}

function sampleSet(destFolder, fileName) {
    if (destFolder === 'jobs') {
        if (fileName.includes('google')) {
            return true;
        }

        if (fileName.includes('dice')) {
            return Math.floor((Math.random() * 100) + 1) === 100 ? true : false;
        }

        return Math.floor((Math.random() * 100) + 1) === 100 ? true : false;
    }

    return true;
}

async function generate() {
    await generateDB('resumes-txt', 'resumes', 'sentences_from_file_lines');
    await generateDB('jobs-txt', 'jobs', 'sentences');
}

generate();