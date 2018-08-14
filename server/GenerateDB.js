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
    files.forEach((fileName) => {
        if (fileName.split('.').pop() === 'txt') {
            console.log(`#${i} Persisting data for: ${fileName}`);

            try {
                var text = fs.readFileSync(path.join(srcDir, fileName)).toString();
                var sentences = await PythonConnector.invoke('sentences', text);
                var data = [];
                sentences.forEach((sent) => data.push({sentence: sent, label: ''}));
                fs.writeFileSync(path.join(dbDir, fileName.split('.')[0] + '.json'), JSON.stringify(data));
            }
            catch (e) {
                console.log('Error in parsing:', fileName, e);
            }
        }
    });
}

generateDB('resumes-txt', 'resumes');
//generateDB('jobs-txt', 'jobs');