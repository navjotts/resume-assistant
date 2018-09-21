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
            console.log('error in fetchJobs()', response);
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

function summary(modelName) {
    $.ajax({
        url: `http://localhost:3000/training/summary`,
        success: function(response) {
            var output = "<div class=\"result_header\">LATEST RESULTS</div>";
            var plots = [];
            var stages = Object.keys(response);
            stages.forEach(stage => {
                var divId = modelName + '_' + stage + '_summary_plot';
                output += "<div id=\"" + divId + "\" style=\"margin:20px;\"></div>";
                var models = Object.keys(response[stage]);
                if (models.length) {
                    var data = [];
                    var scores = Object.keys(response[stage][models[0]]);
                    scores.forEach(scoreType => {
                        var scoreValues = models.map(model => response[stage][model][scoreType]);
                        var trace = {
                            x: models,
                            y: scoreValues,
                            text: scoreValues,
                            textposition: 'auto',
                            name: scoreType,
                            type: 'bar'
                        };
                        data.push(trace);
                    });

                    var layout = {
                        barmode: 'group',
                        title: stage + ' Dataset',
                        titlefont:{
                            family: 'Droid Sans Mono',
                            size: 40,
                            color: '#008000'
                        },
                        xaxis: {
                            title: 'Model',
                            titlefont: {
                                family: 'Droid Sans Mono',
                                size: 25
                            },
                        },
                        yaxis: {
                            title: 'Accuracy',
                            range: [0,101],
                            titlefont: {
                                family: 'Droid Sans Mono',
                                size: 25
                            },
                        },
                    };
                    plots.push({divId, data, layout});
                }
            });
            output += "</div>";
            $('#' + modelName + '_' + 'results').html(output);
            plots.forEach(plot => Plotly.newPlot(plot.divId, plot.data, plot.layout));
        },
        error: function(response) {
            console.log('error in summary()', response);
        }
    });
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

    const TIMEOUT = 60*60; // in seconds (training can take a long time depending on the model)
    $.ajax({
        url: `http://localhost:3000/training/${trainOrTest}/${datasetName}/${modelName}/${modelType}/${featureType}`,
        timeout: TIMEOUT*1000,
        success: function(response) {
            var output = "";

            var score = response['score'];
            if (score) {
                output += "<div class=\"result_header\">SCORE</div><table border=\"1\"><tr><th>precision</th><th>recall</th><th>f1-score</th></tr><tr><td>" +  score['precision'] + "</td><td>" + score['recall'] + "</td><td>" + score['f1_score'] + "</td></tr></table>";
            }

            var report = response['report'];
            if (report) {
                output += "<div class=\"result_header\">REPORT</div><table border=\"1\"><tr><td><div class=\"report\">" + report + "</div></td></tr></table>";
            }

            var misclassifications = response['misclassifications'];
            if (misclassifications) {
                output += "<div class=\"result_header\">MISCLASSIFICATIONS</div><table border=\"1\"><tr><th>Sample</th><th>Actual</th><th>Predicted</th></tr>";
                misclassifications.forEach(each => {
                    output += "<tr><td>" + each['sample'] + "</td><td>" + each['actual_label'] + "</td><td>" + each['pred_label'] + "</td></tr>";
                });
                output += "</table>";
            }

            $('#' + modelName + '_' + 'results').html(output);
        },
        error: function(response) {
            console.log('error in fireTrainingOrTesting()', response);
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
            $('#' + tab + '_content').removeClass().addClass('dashboard_content');
        }
        else {
            $('#' + tab).removeClass().addClass('dashboard_tab');
            $('#' + tab + '_content').removeClass().addClass('no-display');
        }
    });
}

function trainEmbeddings() {
    $.ajax({
        url: `http://localhost:3000/training/embeddings/train`,
        success: function(response) {
            console.log(response);
        },
        error: function(response) {
            console.log('error in trainEmbeddings()', response);
        }
    });
}

// the server now returns an array of {'word', 'coords'}
// I have removed the old 'xcoord', 'ycoord'
// and I have added this new parameter 'coords' => this is an array of whatever coordinates the file has (2 coordinates for embeddings2d.csv, 3 coordinates for embeddings3d.csv)
// so for 2D, 'coords' will be [Number1, Number2] (where Number1 cooresponds to 'xcoord', Number2 cooresponds to 'ycoord')
// and for 3D, 'coords' will be [Number1, Number2, Number3] (where Number1 cooresponds to 'xcoord', Number2 cooresponds to 'ycoord', Number3 cooresponds to 'zcoord')
// -----------------------------------------------------------------------------------------------------------------------------
// once done with 2D, extend the code to start supporting 3D
// (the xcoordinate will be item['coords'][0], and the ycoordinate will be item['coords'][1])
// (the zcoordinate will similarly be item['coords'][2])
function visualize3dEmbeddings() {
    var dimension = 3;
    $.ajax({
        url: `http://localhost:3000/training/embeddings/visualize/${dimension}`,
        success: function(response) {
            var output = "<div id=\"embeddings_plot\" style=\"margin:20px;\"></div>";
            $('#embeddings_visualization').html(output);
            // TODO
            console.log(response);
            console.log('3d Graph Data')


            Plotly.d3.csv('https://raw.githubusercontent.com/plotly/datasets/master/3d-scatter.csv', function(err, rows){
                function unpack(rows, key) {
                    return rows.map(function(row) 
                    { return row[key]; });
                }
            var trace1 = {
            x:unpack(rows, 'x1'),  y: unpack(rows, 'y1'), z: unpack(rows, 'z1'), 
            mode: 'markers',
            marker: {
            size: 12,
            line: {
                color: 'rgba(217, 217, 217, 0.14)',
                width: 0.5
            },
            opacity: 0.8
            },
            type: 'scatter3d'
            };
            var trace2 = {
            x:unpack(rows, 'x2'),  y: unpack(rows, 'y2'), z: unpack(rows, 'z2'), 
            mode: 'markers',
            marker: {
            color: 'rgb(127, 127, 127)',
            size: 12,
            symbol: 'circle',
            line: {
                color: 'rgb(204, 204, 204)',
                width: 1
            },
            opacity: 0.9
            },
            type: 'scatter3d'
            };
            var data = [trace1, trace2];
            var layout = {
                dragmode: false,
                margin: {
                l: 0,
                r: 0,
                b: 0,
                t: 0
            }};
            Plotly.newPlot('myDiv', data, layout);
        });
        },
        error: function(response) {
            console.log('error in trainEmbeddings()', response);
        }
    });
}

function visualize2dEmbeddings() {
    var dimension = 2;
    $.ajax({
        url: `http://localhost:3000/training/embeddings/visualize/${dimension}`,
        success: function(response) {
            var output = "<div id=\"embeddings_plot\" style=\"margin:20px;\"></div>";
            $('#embeddings_visualization').html(output);
            console.log(response)
            console.log('Inside 2d graph')

            words = [];
            var xcoords = [];
            var ycoords = [];
            response.forEach(item => {
                words.push(item['word']);
                xcoords.push(item['coords'][0]);
                ycoords.push(item['coords'][1]);
            });

            data = [{
                x: xcoords,
                y: ycoords,
                text: words,
                type: 'scatter',
                name: 'Embeddings',
                hoverinfo: 'text',
                mode: 'markers',
                marker: {color: 'rgba(200, 50, 100, .7)', size: 16}
            }];

            layout = {
                autosize: false,
                width: 1200,
                height: 1200,
                hovermode:'closest',
                title:'2D Word Embeddings',
                xaxis:{zeroline:false, hoverformat: '.2r'},
                yaxis:{zeroline:false, hoverformat: '.2r'}
            };

            Plotly.newPlot('embeddings_plot', data, layout);

            var plot = document.getElementById('embeddings_plot');
            plot.on('plotly_hover', function (eventdata){
            var points = eventdata.points[0],
                pointNum = points.pointNumber;
                Plotly.Fx.hover('embeddings_plot',[
                    {curveNumber:0, pointNumber:pointNum}
                ]);
            });
        },
        error: function(response) {
            console.log('error in trainEmbeddings()', response);
        }
    });
}

function generateEmbeddingsCoordinates() {
    var dimension = 2;
    const TIMEOUT = 60*60; // in seconds (training can take a long time depending on the model)
    $.ajax({
        url: `http://localhost:3000/training/embeddings/generatecoordinates/${dimension}`,
        timeout: TIMEOUT*1000,
        success: function(response) {
            console.log(response)

        },
        error: function(response) {
            console.log('error in generateEmbeddingsCoordinates()', response);
        }
    });
}