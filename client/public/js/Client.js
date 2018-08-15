function fetchResumes() {
    console.log('Fetching resumes from DB...');
    $.get("http://localhost:3000/training/resumes", function(response) {
        var output = "";
        for (var i = 0; i < response.length; i++) {
            output += "<div id=" + i + " ><a href=\"#\" onclick=\"fetchResume(" + i + ")\">" +  response[i] + "</a></div>";
        }
        $("#list").html(output);
    });
}

function fetchJobs() {
    console.log('Fetching jobs from DB...');
    $.get("http://localhost:3000/training/jobs", function(response) {
        var output = "";
        for (var i = 0; i < response.length; i++) {
            output += "<div id=" + i + " ><a href=\"#\" onclick=\"fetchJob(" + i + ")\">" +  response[i] + "</a></div>";
        }
        $("#list").html(output);
    });
}

function fetchResume(id) {
    console.log(`Fetching resumeId ${id} from DB...`);
    $(location).attr('href', `http://localhost:3000/training/resumes/${id}`);
}

function fetchJob(id) {
    console.log(`Fetching resumeId ${id} from DB...`);
    $(location).attr('href', `http://localhost:3000/training/jobs/${id}`);
}

function updateLabel(option, parentId, docId, sentenceId) {
    console.log(`Updating label ${option.value} for ${sentenceId} for docId ${docId} in ${parentId}...`);
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