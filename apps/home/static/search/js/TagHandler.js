function TagHandler(){
    var tagSuggestions = [];

    this.getTagSuggestions = function(){
        return tagSuggestions;
    };

    var orderTags = function(list){
            var uniqueTags = {};
            list.forEach(function(tag){
                if(uniqueTags.hasOwnProperty(tag)){
                    uniqueTags[tag] += 1;
                } else {
                    uniqueTags[tag] = 1;
                }
            }, this);

            var newList = Object.keys(uniqueTags);
            newList.sort(function(x, y){
                if(uniqueTags[x] < uniqueTags[y]){
                    return 1;
                } else if (uniqueTags[x] > uniqueTags[y]) {
                    return -1;
                } else {
                    return 0;
                }
            });
            return newList;
    };

    this.manageTagSuggestions = function(projects){
        var newTagSuggestions = [];
        var newTagSuggestionsPrio2 = [];
        var newTagSuggestionsPrio3 = [];
        projects.forEach(function(project){
            newTagSuggestions.push.apply(newTagSuggestions, project.tags.prio1);
            newTagSuggestionsPrio2.push.apply(newTagSuggestionsPrio2, project.tags.prio2);
            newTagSuggestionsPrio3.push.apply(newTagSuggestionsPrio3, project.tags.prio3);
        }, this);
        newTagSuggestionsPrio2 = newTagSuggestionsPrio2.filter( function( el ) {
          return newTagSuggestions.indexOf( el ) < 0;
        } );
        newTagSuggestionsPrio3 = newTagSuggestionsPrio3.filter( function( el ) {
          return newTagSuggestions.indexOf( el ) < 0 || newTagSuggestionsPrio2.indexOf( el ) < 0;
        } );

        newTagSuggestions = orderTags(newTagSuggestions);
        newTagSuggestions.push.apply(newTagSuggestions, orderTags(newTagSuggestionsPrio2));
        newTagSuggestions.push.apply(newTagSuggestions, orderTags(newTagSuggestionsPrio3));
        tagSuggestions = newTagSuggestions;
    };
}