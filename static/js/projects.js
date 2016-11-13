/*
 * Create UI elements
 */

function showActiveProjects(projectLoader, $grid) {
    projectLoader.orderProjects();
    $grid.clearGrid();

    projectLoader.getActiveProjects().forEach(function (project) {
        $grid.addContainer(createProjectDiv(project));
    }, this);

    $grid.grid();
}

function appendProjects(projectLoader, $grid) {
    projectLoader.orderNewProjects();

    var appendedItems = [];
    projectLoader.getNewActiveProjects().forEach(function (project) {
        appendedItems.push(createProjectDiv(project));
    }, this);

    $grid.appendContainers(appendedItems);

}

function changeOrder(order) {
    console.log(order);
    if (order == 'most_views') {
        projectLoader.orderViews();
        $('#sort-default').html("Relevanz");
        $('#sort-default').parent().removeClass('active');
        $('#sort-newest').html("Neuste");
        $('#sort-newest').parent().removeClass('active');

        $('#sort-most-views').html('Meistgesehen <i class="fa fa-check" aria-hidden="true">');
        $('#sort-most-views').parent().addClass('active');
    } else if (order == 'newest') {
        projectLoader.orderNewest();
        $('#sort-most-views').html("Meistgesehen");
        $('#sort-most-views').parent().removeClass('active');
        $('#sort-default').html("Relevanz");
        $('#sort-default').parent().removeClass('active');

        $('#sort-newest').html('Neuste <i class="fa fa-check" aria-hidden="true">');
        $('#sort-newest').parent().addClass('active');
    } else {
        projectLoader.orderDefault();
        $('#sort-most-views').html("Meistgesehen");
        $('#sort-most-views').parent().removeClass('active');
        $('#sort-newest').html("Neuste");
        $('#sort-newest').parent().removeClass('active');

        $('#sort-default').html('Relevanz <i class="fa fa-check" aria-hidden="true">');
        $('#sort-default').parent().addClass('active');
    }
    projectLoader.cachingOff();
    projectLoader.getProjects(false);
}

function createProjectDiv(project) {
    var col = $('<div />', {
        'class': 'project-box',
        'id': 'project-' + project.id
    });
    var panel = $('<div />', {
        'class': 'panel'
    });
    var panelBody = $('<div />', {
        'class': 'panel-body'
    });
    var panelImage = $('<div />', {
        'class': 'panel-image'
    });
    var a = $('<a />', {
        'href': '/p/' + project.id
    });
    var img = $('<img />', {
        'class': 'img-responsive',
        'src': project.img
    });
    var panelTitle = $('<div />', {
        'class': 'panel-title'
    });
    var adiv = $('<div />', {
        "onclick": "goToProject(" + project.id + ");"
    });
    var a2 = $('<a />', {
        'href': '/p/' + project.id,
    });
    var heading = $('<span />', {
        'class': 'h2 font-elegance'
    }).text(project.heading);

    col.append(panel);

    if (project.colorNr > 0 && project.colorNr <= 10) {
        adiv.addClass('border-colorful-' + project.colorNr);
    } else {
        adiv.addClass('border-default');
    }
    panel.append(panelBody);
    panelBody.append(panelImage);
    panelImage.append(a);
    panelBody.append(panelTitle);
    a.append(img);
    panelTitle.append(adiv);
    a2.append(heading);
    adiv.append(a2);
    return col;
}
