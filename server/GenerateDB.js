const fs = require('fs');
const path = require('path');

const PythonConnector = require('./PythonConnector.js');

async function generateDB(srcFolder, destFolder) {
    var dbDir = path.join(__dirname, 'data', 'DB', destFolder);
    if (fs.existsSync(dbDir)) {
        console.log(`DB already exists – ${destFolder} ...`);
        return;
    }

    fs.mkdirSync(dbDir);

    var srcDir = path.join(__dirname, 'data', srcFolder);
    var files = fs.readdirSync(srcDir);
    for (var i = 0; i < files.length; i++) {
        var fileName = files[i];
        if (fileName.split('.').pop() === 'txt') {
            console.log(`#${i} Persisting data for: ${fileName}`);

            try {
                var sentences = await PythonConnector.invoke('sentences_from_file', path.join(srcDir, fileName));
                var data = [];
                sentences.forEach((sent) => data.push({sentence: sent, label: ''}));
                fs.writeFileSync(path.join(dbDir, fileName.split('.')[0] + '.json'), JSON.stringify(data));
            }
            catch (e) {
                console.log('Error in parsing:', fileName, e);
            }
        }
    }
}

generateDB('resumes-txt', 'resumes');
//generateDB('jobs-txt', 'jobs');