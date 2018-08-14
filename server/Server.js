const fs = require('fs');
const path = require('path');
const express = require('express');
const bodyParser = require('body-parser');
const assign = require('object-assign');

var app = express();

app.set('views', path.join(__dirname, '..', 'client', 'views'));
app.set('view engine', 'pug');
app.use(express.static(path.join(__dirname, '..', 'client', 'public')));

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

app.use(function(req, res, next) {
	res.header('Access-Control-Allow-Origin', '*');
	res.header('Access-Control-Max-Age', 7200);
	res.header('Access-Control-Allow-Headers', 'X-Requested-With');
	res.header('Access-Control-Allow-Headers', 'Content-Type');
	next();
});

app.get('/', function(req, res) {
    console.log(req.url);
    res.render('index', {title: 'Resume Assistant'});
});

app.get('/training', function(req, res) {
    console.log(req.url);
    res.render('training', {title: 'Resume Assistant'});
});

app.get('/training/resumes', function(req, res, next) {
    console.log(req.url);
    var resumes = [];
    var dbDir = path.join(__dirname, 'data', 'DB', 'resumes');
    var files = fs.readdirSync(dbDir);
    files.forEach((fileName) => resumes.push(fileName.split('.')[0]));
	res.json(resumes);
});

app.get('/training/resumes/:id', function(req, res, next) {
    console.log(req.url);
    var resumeId = req.params.id;
    var dbDir = path.join(__dirname, 'data', 'DB', 'resumes');
    var files = fs.readdirSync(dbDir);
    var fileName = files[resumeId];
    var resumeData = JSON.parse(fs.readFileSync(path.join(dbDir, fileName)));
    res.render('document', {id: resumeId, data: resumeData, title: fileName.split('.')[0]});
});

// TODO error handling inside these
app.post('/training/resumes/:resumeId/sentences/:sentenceId/edit', function(req, res, next) {
    console.log(req.url);
    var resumeId = req.params.resumeId;
    var sentenceId = req.params.sentenceId;
    var label = req.body.label;
    console.log('label', label);

    var dbDir = path.join(__dirname, 'data', 'DB', 'resumes');
    var files = fs.readdirSync(dbDir);
    var fileName = files[resumeId];
    var resumeData = JSON.parse(fs.readFileSync(path.join(dbDir, fileName)));
    resumeData[sentenceId].label = label;
    fs.writeFileSync(path.join(dbDir, fileName), JSON.stringify(resumeData));
    res.json(resumeData[sentenceId]);
});

app.get('*', function(req, res, next) {
    var err = new Error();
    err.status = 404;
    next(err);
});

app.use(function(err, req, res, next) {
    if (err.status !== 404) {
        return next(err);
    }

    res.status(500);
    res.render('error', {error: err});
});

var PORT = 3000;
app.listen(PORT, () => console.log(`Started listening on port ${PORT} ...`));