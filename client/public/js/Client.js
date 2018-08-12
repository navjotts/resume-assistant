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
    console.log('Fetch jobs from DB...');
    alert('not implemented yet!');
}

function uploadResume() {
    alert('not implemented yet!');
}

function uploadJob() {
    alert('not implemented yet!');
}