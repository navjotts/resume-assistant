const fs = require('fs');
const path = require('path');
const jszip = require('jszip');

const DocxParser = require('./DocxParser.js');

async function convertDocxToTxt(srcFolder, destFolder) {
    var files = fs.readdirSync(path.join(__dirname, 'data', srcFolder));
    for (var i = 0; i < files.length; i++) {
        var fileName = files[i];
        var fileNameSplit = fileName.split('.');
        if (fileNameSplit.pop() === 'docx') {
            console.log(`#${i} Parsing: ${fileName}`);

            var destFilePath = path.join(__dirname, 'data', destFolder, fileNameSplit[0] + '.txt');
            if (fs.existsSync(destFilePath)) {
                console.log('Already exists in DB');
            }
            else {
                try {
                    var file = fs.readFileSync(path.join(__dirname, 'data', srcFolder, fileName));
                    var doc = await DocxParser.parseAsync(file);
                    var text = '';
                    doc.forEach(para => text = text + (text.length ? '\n' : '') + para.text);
                    if (text) {
                        fs.writeFileSync(destFilePath, text);
                    }
                }
                catch (e) {
                    console.log('Error in parsing -', fileName, e);
                }
            }
        }
    }
}

convertDocxToTxt('resumes-docx', 'resumes-txt');