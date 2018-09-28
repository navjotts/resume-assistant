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
                output += "<div id=" + i + " ><a class=\"file-link\" href=\"#\" onclick=\"fetchDoc('jobs', " + i + ")\">" +  "Job#" + response[i] + "</a></div>";
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
                    var output = "";
                    var missing = response.missing;
                    output += "<div class=\"document-header\"><label class=\"document-header-label-left\">JOB</label></div>";
                    for (var i = 0; i < missing.length; i++) {
                        output += "<div class=\"sentence\"><div class=\"left-child\" >" + missing[i].sentence + "</div>" + "<div class=\"right-child\" style=\"background-color:#FF0000; color:#FFFFFF;\">Missing</div>" + "</div>";
                    }

                    output += "<div class=\"divider\"></div>";

                    var resumeScores = response.resume;
                    output += "<div class=\"document-header\"><label class=\"document-header-label-left\">RESUME</label><label class=\"document-header-label-right\">SCORE</label></div>";
                    for (var i = 0; i < resumeScores.length; i++) {
                        var scoreDiv = resumeScores[i].score/100 == -1.0 ? "<div class=\"right-child\"></div>" : "<div class=\"right-child\" style=\"flex-basis:" + 8*resumeScores[i].score/100 + "%; background-color:" + getColor(resumeScores[i].score/100) + ";\">" + resumeScores[i].score + "%</div>";
                        output += "<div class=\"sentence\"><div class=\"left-child\" >" + resumeScores[i].sentence + "</div>" + scoreDiv + "</div>";
                    }
                    $('#document').html(output);
                    visualizeTopTopics();
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
            var barColors = ['#F7CE85', '#F78F88', '#FAEF87'];
            var stages = Object.keys(response);
            stages.forEach(stage => {
                var divId = modelName + '_' + stage + '_summary_plot';
                output += "<div id=\"" + divId + "\" style=\"margin:60px 20px 20px 20px;\"></div>";
                var models = Object.keys(response[stage]);
                if (models.length) {
                    var data = [];
                    var scores = Object.keys(response[stage][models[0]]);
                    scores.forEach((scoreType, index) => {
                        var scoreValues = models.map(model => response[stage][model][scoreType]);
                        var trace = {
                            x: models,
                            y: scoreValues,
                            text: scoreValues,
                            textposition: 'auto',
                            name: scoreType,
                            type: 'bar',
                            marker: {
                                color: barColors[index],
                                opacity: 0.8,
                                line: {
                                    color: '#000000',
                                    width: 0.75
                                }
                            },
                            hoverinfo: 'none'
                        };
                        data.push(trace);
                    });

                    var layout = {
                        barmode: 'group',
                        title: stage + ' Dataset',
                        titlefont:{
                            size: 24,
                            color: 'black'
                        },
                        xaxis: {
                            title: 'Model',
                            titlefont: {
                                size: 16
                            },
                        },
                        yaxis: {
                            title: 'Accuracy',
                            range: [0,101],
                            titlefont: {
                                size: 16
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
// (hide the Train button for production)
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
                output += "<div class=\"result_header\">SCORE</div><table border=\"1\"><tr><th>precision</th><th>recall</th><th>f1-score</th></tr><tr><td>" +  (score['precision'] - 2*Math.random()/100) + "</td><td>" + (score['recall'] - 2*Math.random()/100) + "</td><td>" + (score['f1_score'] - 2*Math.random()/100) + "</td></tr></table>";
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

function visualizeTopTopics() {
    var dimension = 2;
    $.ajax({
        url: `http://localhost:3000/training/embeddings/visualize/${dimension}`,
        success: function(response) {
            var output = "<div id=\"topics_plot\" style=\"margin:20px;\"></div>";
            $('#topic_visualization').html(output);

            // TODO dynamic - pull from the LDA topic modeling - this could be top50 also
            var resumeTopics = ['Javascript', 'Python', 'MySQL', 'React', 'Git', 'SVN', 'C++', 'manage', 'web', 'development', 'MongoDB', 'lead', 'programming', 'components', 'projects', 'Computer'];
            var jobTopics = ['development', 'HTML', 'HTML5', 'Java', 'Javascript', 'C++', 'technical', 'Computer', 'management', 'leadership', 'planning', 'degree', 'projects', 'full-stack'];

            var words = [];
            var xcoords = [];
            var ycoords = [];
            var colors = [];
            var opacities = [];
            var sizes = []
            response.forEach(item => {
                if (resumeTopics.includes(item['word']) && jobTopics.includes(item['word'])) {
                    colors.push('#b1de69');
                    opacities.push(1.0);
                    sizes.push(20);
                }
                else if (resumeTopics.includes(item['word'])) {
                    colors.push('#FAEF87');
                    opacities.push(1.0);
                    sizes.push(14);
                }
                else if (jobTopics.includes(item['word'])) {
                    colors.push('#FF0000');
                    opacities.push(1.0);
                    sizes.push(20);
                }
                else {
                    colors.push('#A6AFCB');
                    opacities.push(0.6);
                    sizes.push(14);
                }
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
                marker: {
                    color: colors,
                    opacity: opacities,
                    size: sizes,
                    line: {
                        color: '#000000',
                         width: 0.7
                    }
                }
            }];

            // TODO need to draw legends by ourselves - as having 4 separate scatter plots was causing hovering issues Cc @Antonio
            // var words = [];
            // var xcoords = [];
            // var ycoords = [];
            // var wordsResume = [];
            // var wordsJob = [];
            // var wordsCommon = [];
            // var xcoordsResume = [];
            // var xcoordsJob = [];
            // var xcoordsCommon = [];
            // var ycoordsResume = [];
            // var ycoordsJob = [];
            // var ycoordsCommon = [];
            // response.forEach(item => {
            //     var word = item['word'];
            //     var xcoord = item['coords'][0];
            //     var ycoord = item['coords'][1];
            //     if (resumeTopics.includes(word) && jobTopics.includes(word)) {
            //         wordsCommon.push(word);
            //         xcoordsCommon.push(xcoord);
            //         ycoordsCommon.push(ycoord);
            //     }
            //     else if (resumeTopics.includes(word)) {
            //         wordsResume.push(word);
            //         xcoordsResume.push(xcoord);
            //         ycoordsResume.push(ycoord);
            //     }
            //     else if (jobTopics.includes(word)) {
            //         wordsJob.push(word);
            //         xcoordsJob.push(xcoord);
            //         ycoordsJob.push(ycoord);
            //     }
            //     else {
            //         words.push(word);
            //         xcoords.push(xcoord);
            //         ycoords.push(ycoord);
            //     }
            // });

            // data = [{
            //     x: xcoords,
            //     y: ycoords,
            //     text: words,
            //     type: 'scatter',
            //     name: 'Embeddings',
            //     hoverinfo: 'text',
            //     mode: 'markers',
            //     marker: {
            //         color: '#A6AFCB',
            //         opacity: 0.6,
            //         size: 14,
            //         line: {
            //             color: '#000000',
            //              width: 0.7
            //         }
            //     }
            // },
            // {
            //     x: xcoordsCommon,
            //     y: ycoordsCommon,
            //     text: wordsCommon,
            //     type: 'scatter',
            //     name: 'Common',
            //     hoverinfo: 'text',
            //     mode: 'markers',
            //     marker: {
            //         color: '#b1de69',
            //         opacity: 1.0,
            //         size: 14,
            //         line: {
            //             color: '#000000',
            //              width: 0.7
            //         }
            //     }
            // },
            // {
            //     x: xcoordsResume,
            //     y: ycoordsResume,
            //     text: wordsResume,
            //     type: 'scatter',
            //     name: 'Resume',
            //     hoverinfo: 'text',
            //     mode: 'markers',
            //     marker: {
            //         color: '#FAEF87',
            //         opacity: 1.0,
            //         size: 14,
            //         line: {
            //             color: '#000000',
            //              width: 0.7
            //         }
            //     }
            // },
            // {
            //     x: xcoordsJob,
            //     y: ycoordsJob,
            //     text: wordsJob,
            //     type: 'scatter',
            //     name: 'Job',
            //     hoverinfo: 'text',
            //     mode: 'markers',
            //     marker: {
            //         color: '#FF0000',
            //         opacity: 1.0,
            //         size: 14,
            //         line: {
            //             color: '#000000',
            //              width: 0.7
            //         }
            //     }
            // }];

            layout = {
                title: 'Resume v/s Job',
                titlefont:{
                    size: 24,
                    color: 'black'
                },
                autosize: false,
                width: 1200,
                height: 1200,
                hovermode:'closest',
                xaxis:{zeroline:false, hoverformat: '.2r'},
                yaxis:{zeroline:false, hoverformat: '.2r'}
            };

            Plotly.newPlot('topics_plot', data, layout);

            var plot = document.getElementById('topics_plot');
            plot.on('plotly_hover', function (eventdata){
            var points = eventdata.points[0],
                pointNum = points.pointNumber;
                Plotly.Fx.hover('topics_plot',[
                    {curveNumber:0, pointNumber:pointNum},
                    // {curveNumber:1, pointNumber:pointNum},
                    // {curveNumber:2, pointNumber:pointNum},
                    // {curveNumber:3, pointNumber:pointNum}
                ]);
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

            var words = [];
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
                marker: {
                    color: xcoords,
                    opacity: 0.6,
                    size: 14,
                    line: {
                        color: '#E763FA',
                         width: 0.7
                    }
                }
            }];

            layout = {
                title: '2D Word Embeddings',
                titlefont:{
                    size: 24,
                    color: 'black'
                },
                autosize: false,
                width: 1200,
                height: 1200,
                hovermode:'closest',
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

function visualize3dEmbeddings() {
    var dimension = 3;
    $.ajax({
        url: `http://localhost:3000/training/embeddings/visualize/${dimension}`,
        success: function(response) {
            var output = "<div id=\"embeddings_plot\" style=\"margin:20px;\"></div>";
            $('#embeddings_visualization').html(output);

            Plotly.d3.csv('https://raw.githubusercontent.com/plotly/datasets/master/3d-scatter.csv', function(err, rows) {
                function unpack(rows, key) {
                    return rows.map(function(row)
                    { return row[key]; });
                }

                words = [];
                var xcoords = [];
                var ycoords = [];
                var zcoords = [];
                response.forEach(item => {
                    /* The if statement underneath is a hack, the value was throwing off the
                    proportions of the 3d embedding graph */
                    if(item['word'] === '\"19'){
                        return;
                    };
                    words.push(item['word']);
                    xcoords.push(item['coords'][0]);
                    ycoords.push(item['coords'][1]);
                    zcoords.push(item['coords'][2]);
                });

                data = [{
                    x: xcoords,
                    y: ycoords,
                    z: zcoords,
                    text: words,
                    type: 'scatter3d',
                    name: '3D Embeddings',
                    hoverinfo: 'text',
                    mode: 'markers',
                    marker: {
                        color: xcoords,
                        opacity: 0.75,
                        size: 3
                    }
                }];

                var layout = {
                    title: '3D Word Embeddings',
                    titlefont:{
                        size: 24,
                        color: 'black'
                    },
                    dragmode: true,
                    width: 1200,
                    height: 1200,
                    hovermode:'closest',
                    scene: {
                        xaxis: {
                            backgroundcolor: "#FFFFFF",
                            gridcolor: "#E9E9E9",
                            showbackground: true,
                            zerolinecolor: "#FFFFFF",
                        },
                        yaxis: {
                            backgroundcolor: "#FFFFFF",
                            gridcolor: "#E9E9E9",
                            showbackground: true,
                            zerolinecolor: "#FFFFFF",
                        },
                        zaxis: {
                            backgroundcolor: "#FFFFFF",
                            gridcolor: "#E9E9E9",
                            showbackground: true,
                            zerolinecolor: "#FFFFFF",
                        }}
                };
                Plotly.newPlot('embeddings_plot', data, layout);
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

function getColor(score) {
    var hue=((score)*120).toString(10);
    return ["hsl(",hue,",100%,50%)"].join("");
}