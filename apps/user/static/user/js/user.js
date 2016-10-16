/*
 * Create UI elements
 */


function userHasNoProjects(){
    var alert = $('<div />', {
        'class': "alert alert-danger"
    }).text('Dieser Nutzer hat noch keine Projekte.');
    $('#projects-area').append(alert);
}