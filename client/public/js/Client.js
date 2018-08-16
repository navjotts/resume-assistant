function fetchResumes() {
    $.get("http://localhost:3000/training/resumes", function(response) {
        var output = "";
        for (var i = 0; i < response.length; i++) {
            output += "<div id=" + i + " ><a href=\"#\" onclick=\"fetchResume(" + i + ")\">" +  "Resume#" + i + "</a></div>";
        }
        $("#training-list").html(output);
    });
}

function fetchJobs() {
    $.get("http://localhost:3000/training/jobs", function(response) {
        var output = "";
        for (var i = 0; i < response.length; i++) {
            output += "<div id=" + i + " ><a href=\"#\" onclick=\"fetchJob(" + i + ")\">" +  "Job#" + i + "</a></div>";
        }
        $("#training-list").html(output);
    });
}

function fetchResume(id) {
    $(location).attr('href', `http://localhost:3000/training/resumes/${id}`);
}

function fetchJob(id) {
    $(location).attr('href', `http://localhost:3000/training/jobs/${id}`);
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

function uploadResume() {
    alert('uploadResume() not implemented yet!');
}

function uploadJob() {
    alert('uploadJob() not implemented yet!');
}