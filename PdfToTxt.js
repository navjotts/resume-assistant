const fs = require('fs');
const path = require('path');

const pdfParser = require('pdf-to-text');
const util = require('util');
const pdfToText = util.promisify(pdfParser.pdfToText);

const PythonConnector = require('./PythonConnector.js');

async function convertPdfToTxt(srcFolder, destFolder, filePrefix) {
    var files = fs.readdirSync(path.join(__dirname, 'data', srcFolder));
    for (var i = 0; i < files.length; i++) {
        var fileName = files[i];
        if (fileName.split('.').pop() === 'pdf') {
            console.log(`#${i} Parsing: ${fileName}`);

            try {
                text = await pdfToText(path.join(__dirname, 'data', srcFolder, fileName));
                if (text) {
                    fs.writeFileSync(path.join(__dirname, 'data', destFolder, filePrefix + i + '.txt'), text);
                }
            }
            catch (e) {
                console.log('Error in parsing -', fileName);
            }
        }
    }
}

convertPdfToTxt('resumes-pdf', 'resumes-txt', 'resume-');