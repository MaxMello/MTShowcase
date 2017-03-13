function createAddContentDiv() {

    var contentChoose = $('<div />', {
        'class': 'row'
    }).css({

    });
    var space = $('<div />', {
        'class': 'col-xs-1 hidden-xs hidden-sm'
    });

    var contentText = $('<div />', {
        'class': 'col-xs-4 col-sm-4 col-md-2 col-lg-2 text-center btn-primary btn-lg content-upload-border'
    });

    var contentImage = $('<div />', {
        'class': 'col-lg-2 col-md-2 col-sm-4 col-xs-4 text-center btn-primary btn-lg content-upload-border'
    });

    var contentVideo = $('<div />', {
        'class': 'col-lg-2 col-md-2 col-sm-4 col-xs-4 text-center btn-primary btn-lg content-upload-border'
    });

    var contentAudio = $('<div />', {
        'class': 'col-lg-2 col-md-2 col-sm-6 col-xs-6 text-center btn-primary btn-lg content-upload-border'
    });

    var contentSlideshow = $('<div />', {
        'class': 'col-lg-2 col-md-2 col-sm-6 col-xs-6 text-center btn-primary btn-lg content-upload-border'
    });

    var textIcon = $('<span />', {
        'class': 'fa fa-font' //quote-right font
    });
    var imageIcon = $('<span />', {
        'class': 'fa fa-picture-o'
    });
    var videoIcon = $('<span />', {
        'class': 'fa fa-video-camera' //film
    });
    var audioIcon = $('<span />', {
        'class': 'fa fa-headphones'
    });
    var slideshowIcon = $('<span />', {
        'class': 'fa fa-clone'
    });

    contentText.append(textIcon);
    contentImage.append(imageIcon);
    contentVideo.append(videoIcon);
    contentAudio.append(audioIcon);
    contentSlideshow.append(slideshowIcon);
    contentChoose.append(space);
    contentChoose.append(contentText);
    contentChoose.append(contentImage);
    contentChoose.append(contentVideo);
    contentChoose.append(contentAudio);
    contentChoose.append(contentSlideshow);
    return contentChoose;
}