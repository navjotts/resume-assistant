const fs = require('fs');
const path = require('path');
const jszip = require('jszip');

const DocxParser = require('./DocxParser.js');

async function convertDocxToTxt(srcFolder, destFolder, filePrefix) {
    var files = fs.readdirSync(path.join(__dirname, 'data', srcFolder));
    for (var i = 0; i < files.length; i++) {
        var fileName = files[i];
        if (fileName.split('.').pop() === 'docx') {
            console.log(`#${i} Parsing: ${fileName}`);

            try {
                var file = fs.readFileSync(path.join(__dirname, 'data', srcFolder, fileName));
                var doc = await DocxParser.parseAsync(file);
                var text = '';
                doc.forEach(para => text = text + (text.length ? '\n' : '') + para.text);
                if (text) {
                    fs.writeFileSync(path.join(__dirname, 'data', destFolder, filePrefix + i + '.txt'), text);
                }
            }
            catch (e) {
                console.log('Error in parsing -', fileName, e);
            }
        }
    }
}

convertDocxToTxt('resumes-docx', 'resumes-txt', 'resume-');