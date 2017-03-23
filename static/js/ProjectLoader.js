function ProjectLoader() {
    var that = this;
    var projects = [];
    var activeProjects = [];
    var oldActiveProjects = [];
    var newActiveProjects = [];
    var activeTags = [];
    var lastTagAdded = null;
    var user = null;
    var caching = true;
    var order = 'default';
    var ajaxSuccess = function () {
    };
    var failedSearch = function () {
    };
    var loadMoreProjectsSuccess = function () {
    };
    var loadMoreProjectsFailure = function () {
    };
    const ABSOLUTE_MAXIMUM = 50;
    var maximum = 30;

    this.orderProjects = function () {
        activeProjects.sort(function (x, y) {
            if (x.order > y.order) {
                return 1;
            } else if (x.order < y.order) {
                return -1;
            } else {
                return 0;
            }
        });
        return that;
    };

    this.orderNewProjects = function () {
        newActiveProjects.sort(function (x, y) {
            if (x.order > y.order) {
                return 1;
            } else if (x.order < y.order) {
                return -1;
            } else {
                return 0;
            }
        });
        return that;
    };

    this.setProjectColors = function (tagSuggestions) {
        var first10 = tagSuggestions.slice(0, 10);
        //console.log(first10);
        activeProjects.forEach(function (project) {
            var hasColor = false;
            var tagalikes = [];
            tagalikes.push.apply(tagalikes, project.tags.prio1);
            tagalikes.push.apply(tagalikes, project.tags.prio2);
            tagalikes.push.apply(tagalikes, project.tags.prio3);

            for (var i = 0; i < first10.length; i++) {
                if (hasColor) {
                    break;
                }
                for (var t = 0; t < tagalikes.length; t++) {
                    //console.log(tagalikes[t] + " --- " + first10[i]);
                    if (tagalikes[t].toLowerCase() == first10[i].toLowerCase()) {
                        console.log("Gleich");
                        project['colorNr'] = i + 1;
                        hasColor = true;
                        break;
                    }
                }
            }
        }, this);
        return that;
    };

    this.setActiveTags = function (tags) {
        var oldActiveTags = activeTags;
        activeTags = (typeof tags === 'undefined' || tags === null || tags.constructor !== Array) ? [] : tags;

        activeTags.forEach(function (tag) {
            if (oldActiveTags.indexOf(tag) == -1) {
                lastTagAdded = tag;
            }
        }, this);
        return that;
    };

    this.setUser = function (userID) {
        user = (typeof userID === 'undefined') ? null : userID;
        return that;
    };

    this.orderDefault = function () {
        order = 'default';
        return that;
    };

    this.orderViews = function () {
        order = 'most_views';
        return that;
    };

    this.orderNewest = function () {
        order = 'newest';
        return that;
    };

    this.setMaximum = function (max) {
        maximum = (typeof max === 'undefined' || max === null || typeof max !== 'number' || max > ABSOLUTE_MAXIMUM)
            ? ABSOLUTE_MAXIMUM : Math.abs(Math.floor(max));
        return that;
    };

    this.cachingOn = function () {
        caching = true;
        return that;
    };

    this.cachingOff = function () {
        caching = false;
        return that;
    };

    this.getActiveProjects = function () {
        return activeProjects;
    };

    this.getNewActiveProjects = function () {
        return newActiveProjects;
    };

    this.getOldActiveProjects = function () {
        return oldActiveProjects;
    };

    this.getLastTagAdded = function () {
        return lastTagAdded;
    };

    this.onAjaxSuccess = function (functions) {
        ajaxSuccess = (typeof functions === 'undefined' || functions === null || !$.isFunction(functions)) ? function () {
        } : functions;
        return that;
    };

    this.onFailedSearch = function (functions) {
        failedSearch = (typeof functions === 'undefined' || functions === null || !$.isFunction(functions)) ? function () {
        } : functions;
        return that;
    };

    this.onLoadMoreProjectsSuccess = function (functions) {
        loadMoreProjectsSuccess = (typeof functions === 'undefined' || functions === null || !$.isFunction(functions)) ? function () {
        } : functions;
        return that;
    };

    this.onLoadMoreProjectsFailure = function (functions) {
        loadMoreProjectsFailure = (typeof functions === 'undefined' || functions === null || !$.isFunction(functions)) ? function () {
        } : functions;
        return that;
    };

    this.getProjects = function (append_projects) {
        var append = (typeof append_projects !== 'boolean') ? false : append_projects;
        if (append) {
            // If we append projects, we have to cache the old ones or duplicates will happen
            caching = true;
        }
        var project_ids = [];
        if (caching) {
            //If we cache the old results, we need to filter them frontend as well
            filterProjects();
            projects.forEach(function (project) {
                project_ids.push(project.id);
            }, this);
        }
        var ajaxData = {
            parameters: JSON.stringify({tags: activeTags, except: project_ids, user_id: user, order: order, maximum: maximum}),
            csrfmiddlewaretoken: window.CSRF_TOKEN
        };
        //console.log(ajaxData);
        $.ajax({
            url: "/search/",
            dataType: 'json',
            type: 'POST',
            data: ajaxData,
            success: function (data) {
                //console.log(data);
                newActiveProjects = data.projects;
                var newOldActiveProjects = activeProjects;
                if (caching) {
                    activeProjects = activeProjects.concat(data.projects);
                    projects = projects.concat(data.projects);
                } else {
                    activeProjects = data.projects;
                    projects = data.projects;
                }
                if (append) {
                    if (data.projects.length > 0) {
                        loadMoreProjectsSuccess();
                    } else {
                        loadMoreProjectsFailure();
                    }
                } else {
                    if (activeProjects.length == 0) {
                        activeProjects = oldActiveProjects;
                        failedSearch();
                    } else {
                        //console.log("Ajax success");
                        ajaxSuccess();
                    }
                }
                oldActiveProjects = newOldActiveProjects;
            },
            error: function (request, status, error) {
                //console.log("Ajax Request Error - Status: " + status, " - Error: " + error);
            }
        });
    };

    var filterProjects = function () {
        var filterProject = function (project) {
            var showProject = true;
            activeTags.forEach(function (tag) {
                if (project.search_string.toLowerCase().indexOf(tag.toLowerCase()) == -1) {
                    showProject = false;
                }
            }, this);
            return showProject;
        };

        if (projects.length > 0) {
            var newActiveProjects = [];
            projects.forEach(function (project) {
                var showProject = filterProject(project);
                if (showProject) {
                    newActiveProjects.push(project);
                }
            }, this);
            oldActiveProjects = activeProjects;
            activeProjects = newActiveProjects;
        }
    };
}