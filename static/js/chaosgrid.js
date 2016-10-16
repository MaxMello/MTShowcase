function ChaosGrid() {

    var that = this;
    var breakpoints = new Array();

    var currentBreakpoint = null;
    var oldBreakpoint = null;

    var containers = new Array();

    this.addBreakpoint = function(bpObj) {
        breakpoints.push(bpObj);
        breakpoints.sort(function(a,b) {return a.width-b.width});
        that.checkGrid();
    }

    var gridSelector = $("#projects-row");

    // Use if only one container should be added (if multiple containers should be added, always use appendContainers!)
    this.appendContainer = function(newContainer) {
        containers.push(newContainer);
        that.showControlContainer(containers.length-1);
    }

    // recommended, use if containers should be added to the grid
    this.appendContainers = function(newContainers) {
        for (var i = 0; i < newContainers.length; i++) {
            containers.push(newContainers[i]);
        }
        that.showControlContainer(containers.length-newContainers.length);
    }

    this.addContainer = function (newContainer) {
        containers.push(newContainer);
    }

    this.clearGrid = function() {
        containers = new Array();
        gridSelector.empty();

    }

    this.checkGrid = function() {

        if (breakpoints.length == 0) {
            oldBreakpoint = null;
            currentBreakpoint = null;
            return;
        }

        var currentWindowWidth = $(window).width();

        for (var i = 0; i < breakpoints.length; i++) {
            if (currentWindowWidth <= breakpoints[i].width || i == breakpoints.length-1) {
                oldBreakpoint = currentBreakpoint;
                currentBreakpoint = breakpoints[i];
                break;
            }
        }

        that.grid(false);
    }

    this.grid = function(force) {
        if (currentBreakpoint === null) {
            return;
        }

        force = typeof force !== 'undefined' ? force : true;

        if (force || (oldBreakpoint === null || currentBreakpoint.width != oldBreakpoint.width)) {

            oldBreakpoint = currentBreakpoint;

            gridSelector.empty();

            if (currentBreakpoint.cols <= 0) {
                return;
            }

            for (var i = 1; i <= currentBreakpoint.cols; i++) {
                gridSelector.append($('<div />', {
                    'class': currentBreakpoint.use,
                    'id': 'chaosgridcol-' + i
                }));
            }

            if (containers.length > 0) {
                that.showControlContainer(0);
            }

        }

    }

    this.showControlContainer = function(currentContainer) {

        if (currentContainer < containers.length) {

            var colHeights = new Array();

            for (var i = 1; i <= currentBreakpoint.cols; i++) {
                colHeights.push({col: i, height: $("#chaosgridcol-"+i).height()});
            }
            colHeights.sort(function(a,b) {return a.height-b.height});

            $("#chaosgridcol-"+colHeights[0].col).append(containers[currentContainer]);

            $("#chaosgridcol-"+colHeights[0].col).imagesLoaded(function() {
                that.showControlContainer(currentContainer+1);
            })

        }

    }

    $(window).resize(function() {
        that.checkGrid();
    });

}
