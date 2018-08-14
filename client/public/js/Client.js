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

function fetchResume(id) {
    console.log(`Fetching resumeId ${id} from DB...`);
    $(location).attr('href', `http://localhost:3000/training/resumes/${id}`);
}

function fetchJobs() {
    console.log('Fetching jobs from DB...');
    alert('fetchJobs() not implemented yet!');
}

function updateLabel(option, resumeId, sentenceId) {
    console.log(`Updating label ${option.value} for ${sentenceId} for resumeId ${resumeId}...`);
    $.ajax({
        url: `http://localhost:3000/training/resumes/${resumeId}/sentences/${sentenceId}/edit`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            label:option.value
        }),
        dataType: 'json',
        success: function(response) {
            fetchResume(resumeId);
        }
    });
}

function uploadResume() {
    alert('uploadResume() not implemented yet!');
}

function uploadJob() {
    alert('uploadJob() not implemented yet!');
}