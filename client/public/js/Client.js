function loadTraining() {
    $(location).attr('href', `http://localhost:3000/training`);
}

function fetchResumes() {
    $.get("http://localhost:3000/training/resumes", function(response) {
        var output = "";
        for (var i = 0; i < response.length; i++) {
            output += "<div id=" + i + " ><a href=\"#\" onclick=\"fetchDoc('resumes', " + i + ")\">" +  "Resume#" + i + "</a></div>";
        }
        $("#training-list").html(output);
    });
}

function fetchJobs() {
    $.get("http://localhost:3000/training/jobs", function(response) {
        var output = "";
        for (var i = 0; i < response.length; i++) {
            output += "<div id=" + i + " ><a href=\"#\" onclick=\"fetchDoc('jobs', " + i + ")\">" +  "Job#" + i + "</a></div>";
        }
        $("#training-list").html(output);
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
            var files = {resume: resumeFileName, job: jobFileName};
            $.get(`http://localhost:3000/analyze/${resumeFileName}/${jobFileName}`, function(response) {
                var output = "";
                for (var i = 0; i < response.length; i++) {
                    output += "<div class=\"sentence\" ><div class=\"left-child\" >" + response[i].sentence + "</div><div class=\"right-child\" >" + response[i].label + " (" + response[i].confidence + "%)" + "</div></div>";
                }
                $("#document").html(output);
            });
        }
    }

    var resumeFiles = $("#resume-file")[0].files;
    var jobFiles = $("#job-file")[0].files;
    if (resumeFiles.length !== 1 || jobFiles.length !== 1) {
        alert('Please select 1 resume and 1 job description to analyze!');
        return;
    }

    var resumeFileData = new FormData();
    resumeFileData.append('userFile', resumeFiles[0]);
    $.ajax({
        url: "http://localhost:3000/upload",
        type: 'POST',
        data: resumeFileData,
        processData: false,
        contentType: false,
        success: function(response) {
            // TODO need error handling here
            console.log("analyzeFiles()", response);
            resumeFileName = resumeFiles[0].name;
            analyzeIfReady();
        }
    });

    var jobFileData = new FormData();
    jobFileData.append('userFile', jobFiles[0]);
    $.ajax({
        url: "http://localhost:3000/upload",
        type: 'POST',
        data: jobFileData,
        processData: false,
        contentType: false,
        success: function(response) {
            // TODO need error handling here
            console.log("analyzeFiles()", response);
            jobFileName = jobFiles[0].name;
            analyzeIfReady();
        }
    });
}

function showFilePickerForInput(id) {
    $(`#${id}`).click();
}