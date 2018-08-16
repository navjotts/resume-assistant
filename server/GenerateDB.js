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
                        var text = fs.readFileSync(path.join(srcDir, fileName)).toString();
                        sentences = await PythonConnector.invoke('sentences', text);
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

async function generate() {
    await generateDB('resumes-txt', 'resumes', 'sentences_from_file_lines');
    await generateDB('jobs-txt', 'jobs', 'sentences');
}

generate();