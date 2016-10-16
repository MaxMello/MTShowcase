/*
 * Create UI elements
 */

function showTagSuggestions(tagHandler){
        $('.tag-btn').each(function(i, obj) {
            $(this).remove();
        });

        var count = 0;
        tagHandler.getTagSuggestions().forEach(function(tag){
            if($("#tag-bar").tagit("assignedTags").indexOf(tag) == -1 && count < 10){
                $('#tag-suggestions').append(createTagButton(tag, count+1));
                count++;
            }
        }, this);
}

function showFailedSearch(){
    var lastTagAdded = $("#tag-bar").tagit("getLastTag");
    lastTagAdded.addClass("tagit-choice-no-result shake");
    var tagSpan = lastTagAdded.find(".tagit-label");
    /*
    tagSpan.attr("data-toggle","popover");
    tagSpan.attr("data-placement", "bottom");
    tagSpan.attr("data-container", "body");
    tagSpan.attr("data-trigger", "manual");
    tagSpan.attr("data-content","Kein Ergebnis");
    $(tagSpan).popover();
    $(tagSpan).popover("show");
    */
    setTimeout(function () {
        //$(tagSpan).popover("hide");
        $("#tag-bar").tagit("removeTag", lastTagAdded, true, false);
    }, 1000);
}

function createTagButton(tag, colorNr){
    var button = $('<button />', {
        'class': 'btn tag-btn btn-colorful-'+colorNr,
        'id': tag
    }).text(tag);
    return button;
}