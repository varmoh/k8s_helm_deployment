function loadConfig() {
    var formData = new FormData($('#configForm')[0]);
    $.ajax({
        url: '/load_config',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.status === 'success') {
                var releases = response.releases;
                var releasesDiv = $('#releases');
                releasesDiv.empty();
                releases.forEach(function(release) {
                    releasesDiv.append(`
                        <input type="checkbox" name="selectedReleases" value="${release}">${release}<br>
                    `);
                });
                $('#deployForm').show();
                $('#message').text('Configuration loaded successfully.').addClass('success-message').removeClass('status-message');
            } else {
                $('#message').text(response.message).addClass('status-message').removeClass('success-message');
            }
        },
        error: function(response) {
            $('#message').text(response.responseJSON.message).addClass('status-message').removeClass('success-message');
        }
    });
}

function deploy() {
    var formData = new FormData($('#deployForm')[0]);
    formData.append('configFile', $('#configFile')[0].files[0]);
    $.ajax({
        url: '/deploy',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            $('#message').text(response.message).addClass('success-message').removeClass('status-message');
        },
        error: function(response) {
            $('#message').text(response.responseJSON.message).addClass('status-message').removeClass('success-message');
        }
    });
}

function startLogStream() {
    var eventSource = new EventSource('/logs');
    eventSource.onmessage = function(event) {
        var logContainer = $('#logContainer');
        var logLines = event.data.split('\n');
        logLines.forEach(function(line) {
            if (line.trim()) {
                var logClass = line.includes('ERROR') ? 'error' : 'info';
                logContainer.append(`<div class="log-entry ${logClass}">${line}</div>`);
                logContainer.scrollTop(logContainer[0].scrollHeight); // Auto-scroll to bottom
            }
        });
    };
    eventSource.onerror = function(event) {
        $('#logContainer').append('<div class="log-entry error">Error fetching logs.</div>');
    };
}

$(document).ready(function() {
    startLogStream();
});
