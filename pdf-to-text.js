var fs = require('fs');
var path = require('path')
var pdfParser = require('pdf-to-text');

var util = require('util');
var pdfToText = util.promisify(pdfParser.pdfToText);

async function generateTextCorpus() {
  var files = fs.readdirSync(path.join(__dirname, 'data', 'resumes-pdf'))

  for (var i=0; i<files.length; i++) {
    var fileName = files[i];
    if (fileName.split('.').pop() === 'pdf') {
      console.log('Parsing #' + i + ' - ' + fileName);

      try {
        resumeText = await pdfToText(path.join(__dirname, 'data', 'resumes-pdf', fileName));
        if (resumeText) {
          fs.writeFileSync(path.join(__dirname, 'data', 'resumes-txt', 'resume-' + i + '.txt'), resumeText);
        }
      }
      catch (e) {
        console.log('Error in parsing -', fileName);
      }
    }
  }
}

generateTextCorpus();