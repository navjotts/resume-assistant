function loadTraining() {
    $(location).attr('href', `http://localhost:3000/training`);
}

function fetchResumes() {
    $.ajax({
        url: `http://localhost:3000/training/resumes`,
        success: function(response) {
            var output = "";
            for (var i = 0; i < response.length; i++) {
                output += "<div id=" + i + " ><a class=\"file-link\" href=\"#\" onclick=\"fetchDoc('resumes', " + i + ")\">" +  "Resume#" + i + "</a></div>";
            }
            $('#resumes-list').html(output);
        },
        error: function(response) {
            console.log('error in fetchResumes()', response);
        }
    });
}

function fetchJobs() {
    $.ajax({
        url: `http://localhost:3000/training/jobs`,
        success: function(response) {
            var output = "";
            for (var i = 0; i < response.length; i++) {
                output += "<div id=" + i + " ><a class=\"file-link\" href=\"#\" onclick=\"fetchDoc('jobs', " + i + ")\">" +  "Job#" + i + "</a></div>";
            }
            $('#jobs-list').html(output);
        },
        error: function(response) {
            console.log('error in fetchResumes()', response);
        }
    });
}

function fetchDoc(parentId, id) {
    $(location).attr('href', `http://localhost:3000/training/${parentId}/${id}`);
}

function updateLabel(option, parentId, docId, sentenceId) {
    $.ajax({
        url: `http://localhost:3000/training/${parentId}/${docId}/sentences/${sentenceId}/edit`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            label:option.value
        }),
        dataType: 'json',
        success: function(response) {}
    });
}

function analyzeFiles() {
    var resumeFileName, jobFileName;
    function analyzeIfReady() {
        if (resumeFileName && jobFileName) {
            $('#analyze_button').text('ANALYZING...');
            var files = {resume: resumeFileName, job: jobFileName};
            $.ajax({
                url: `http://localhost:3000/analyze/${resumeFileName}/${jobFileName}`,
                success: function(response) {
                    var output = "<div class=\"document-header\"><label class=\"document-header-label-left\">SENTENCE / PHRASE</label><label class=\"document-header-label-right\">PREDICTION (Confidence%)</label></div>";
                    for (var i = 0; i < response.length; i++) {
                        output += "<div class=\"sentence\"><div class=\"left-child\" >" + response[i].sentence + "</div><div class=\"right-child\" >" + response[i].label + " (" + response[i].confidence + "%)" + "</div></div>";
                    }
                    $('#document').html(output);
                    $('#analyze_button').text('START ANALYZING');
                },
                error: function(response) {
                    console.log('error in analyzeIfReady()', response);
                }
            });
        }
    }

    var resumeFiles = $('#resume-file')[0].files;
    var jobFiles = $('#job-file')[0].files;
    if (resumeFiles.length !== 1 || jobFiles.length !== 1) {
        alert('Please select 1 resume and 1 job description to analyze!');
        return;
    }

    $('#analyze_button').text('UPLOADING...');
    var resumeFileData = new FormData();
    resumeFileData.append('userFile', resumeFiles[0]);
    $.ajax({
        url: `http://localhost:3000/upload`,
        type: 'POST',
        data: resumeFileData,
        processData: false,
        contentType: false,
        success: function(response) {
            // TODO need error handling here
            console.log('analyzeFiles()', response);
            resumeFileName = resumeFiles[0].name;
            analyzeIfReady();
        }
    });

    var jobFileData = new FormData();
    jobFileData.append('userFile', jobFiles[0]);
    $.ajax({
        url: `http://localhost:3000/upload`,
        type: 'POST',
        data: jobFileData,
        processData: false,
        contentType: false,
        success: function(response) {
            // TODO need error handling here
            console.log('analyzeFiles()', response);
            jobFileName = jobFiles[0].name;
            analyzeIfReady();
        }
    });
}

function showFilePicker(inputId) {
    $(`#${inputId}`).click();
}

function showFilePicked(inputId, labelId) {
    var files = $(`#${inputId}`)[0].files;
    if (files.length == 1) {
        $(`#${labelId}`).text(files[0].name);
    }
}

// TODO need an option to NOT really fire any training when the call is from the production URL (as then we have to manage the saving of the updated model weights etc)
function train(modelName) {
    fireTrainingOrTesting('train', modelName);
}

function test(modelName) {
    fireTrainingOrTesting('test', modelName);
}

function fireTrainingOrTesting(trainOrTest, modelName) {
    var model = selectedModelType(modelName);
    if (!model) {
        alert(`Please select a model to ${trainOrTest}`);
        return;
    }

    var modelType = model.value;

    var featureType = 'None';
    var feature = selectedFeatureType(modelName);
    if (feature) {
        featureType = feature.value;
    }

    var datasetName = 'DB';
    var dataset = selectedDataset(modelName);
    if (dataset) {
        datasetName = dataset.value;
    }

    console.log(`${trainOrTest} (dataset, model, feature): (${datasetName}, ${modelType}, ${featureType})`);

    $.ajax({
        url: `http://localhost:3000/training/${trainOrTest}/${datasetName}/${modelName}/${modelType}/${featureType}`,
        success: function(response) {
            var output = "";

            var score = response['score'];
            if (score) {
                output += "<table border=\"1\"><tr><th>precision</th><th>recall</th><th>f1-score</th></tr><tr><td>" +  score['precision'] + "</td><td>" + score['recall'] + "</td><td>" + score['f1_score'] + "</td></tr></table>";
            }

            var report = response['report'];
            if (report) {
                output += "<table border=\"1\"><tr><td><div class=\"report\">" + report + "</div></td></tr></table>";
            }

            var misclassifications = response['misclassifications'];
            if (misclassifications) {
                output += "<table border=\"1\"><tr><th>Sample</th><th>Actual</th><th>Predicted</th></tr>";
                misclassifications.forEach(each => {
                    output += "<tr><td>" + each['sample'] + "</td><td>" + each['actual_label'] + "</td><td>" + each['pred_label'] + "</td></tr>";
                });
                output += "</table>";
            }

            $('#' + modelName + '_' + 'results').html(output);
        },
        error: function(response) {
            console.log('error in test()', response);
        }
    });
}

function selectedModelType(modelName) {
    var model;
    var formName = modelName + 'ModelForm';
    var inputName = modelName + 'ModelType';
    var radios = document[formName][inputName];
    radios.forEach(rad => {
        if (rad.checked) {
            model = rad;
        }
    });

    return model;
}

function selectedFeatureType(modelName) {
    var feature;
    var formName = modelName + 'FeatureForm';
    var inputName = modelName + 'FeatureType';
    var radios = document[formName][inputName];
    radios.forEach(rad => {
        if (rad.checked) {
            feature = rad;
        }
    });

    return feature;
}

function selectedDataset(modelName) {
    var dataset;
    var formName = modelName + 'DatasetForm';
    var inputName = modelName + 'Dataset';
    var radios = document[formName][inputName];
    radios.forEach(rad => {
        if (rad.checked) {
            dataset = rad;
        }
    });

    return dataset;
}


function selectDashboardTab(selectedTab) {
    ['resumes_tab', 'jobs_tab', 'comparison_tab'].forEach(tab => {
        if (selectedTab == tab) {
            $('#' + tab).removeClass().addClass('dashboard_tab_focussed');
            $('#' + tab + '_content').removeClass().addClass('dashboard_tab_content');
        }
        else {
            $('#' + tab).removeClass().addClass('dashboard_tab');
            $('#' + tab + '_content').removeClass().addClass('no-display');
        }
    });
}