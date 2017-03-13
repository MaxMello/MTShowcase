var addcontentchoice;
var addcontent;
var supervisor_wrapper = $('#supervisor-wrapper');
var supervisor_input_uid = 0;
var member_wrapper = $('#member-wrapper');
var users_responsibilities = {};
var content_btn = $('#content-btn');
var body_element = $('body');
var crop_data;

$.fn.cropper();


// region addcontent choices click handler & hover
content_btn.on("click", "#addText", function () {
    $.getJSON(addContentTextUrl, function (json) {
        content_btn.before(json.text);
    });
});

content_btn.on("click", "#addPicture", function () {
    $.getJSON(addContentPictureUrl, function (json) {
        content_btn.before(json.text);
    });
});

content_btn.on("click", "#addVideo", function () {
    $.getJSON(addContentVideo, function (json) {
        content_btn.before(json.text);
    });
});

content_btn.on("click", "#addAudio", function () {
    $.getJSON(addContentAudio, function (json) {
        content_btn.before(json.text);
    });
});

content_btn.on("click", "#addSlideshow", function () {
    $.getJSON(addSlideshowUrl, function (json) {
        content_btn.before(json.text);
        setUpDropzoneContainerForSlideshow();
    });
});

content_btn.on("mouseenter", "#addcontent-row", function () {
    $(this).replaceWith(addcontentchoice);
});

content_btn.on("mouseleave", "#addcontentchoice-row", function () {
    $(this).replaceWith(addcontent);
});

//endregion

// ############## LEFT PANE ##############

// region addImage functionality
body_element.on("click", ".addImageLink", function () {
    var $that = $(this);
    $.getJSON(imageLinkUrl, function (json) {
        var container = $that.parent().parent().find('.input-container');
        container.append(json.text);
    });
});

body_element.on("click", ".addImageFile", function () {
    var $that = $(this);
    $.getJSON(imageFileUrl, function (json) {
        var container = $that.parent().parent().find('.input-container');
        container.append(json.text);
        $(".image-file-input").find(":file").filestyle({
            buttonText: "",
            buttonName: "btn-primary",
            iconName: "fa fa-file-image-o",
            buttonBefore: true,
            placeholder: "Keine Datei ausgewählt."
        });
    });

});

body_element.on("click", ".startCrop", function () {
    var $img = $(this).parent().siblings('.add_content_image');
    $img.cropper({zoomable:false, zoomOnWheel:false});
    $(this).next().prop("disabled", false);
});

body_element.on("click", ".crop_button", function () {
    var $img = $(this).parent().siblings('.add_content_image');
    $img.siblings('input').val(JSON.stringify($img.cropper("getData")));
    var imgUrl = $img.cropper('getCroppedCanvas').toDataURL();
    $img.cropper("destroy");
    $img.attr("src", imgUrl);
    $(this).prop("disabled", true);
});
// endregion

// region addVideo functionality
body_element.on("click", ".addVideoFile", function () {
    var $that = $(this);
    $.getJSON(addVideoFileUrl, function (json) {
        var container = $that.parent().parent().find('.input-container');
        container.append(json.text);

        $(".video-input").find(":file").filestyle({
            buttonText: "",
            buttonName: "btn-primary",
            iconName: "fa fa-file-video-o",
            buttonBefore: true,
            placeholder: "Keine Datei ausgewählt."
        });
    });
});

body_element.on("click", ".addVideoLink", function () {
    var $that = $(this);
    $.getJSON(addVideoLinkUrl, function (json) {
        var container = $that.parent().parent().find('.input-container');
        container.append(json.text);
    });

});
// endregion

// region addAudio functionality
body_element.on("click", ".addAudioFile", function () {
    var $that = $(this);
    $.getJSON(addAudioFileUrl, function (json) {
        var container = $that.parent().parent().find('.input-container');
        container.append(json.text);

        $(".audio-input").find(":file").filestyle({
            buttonText: "",
            buttonName: "btn-primary",
            iconName: "fa fa-file-audio-o",
            buttonBefore: true,
            placeholder: "Keine Datei ausgewählt."
        });
    });
});

body_element.on("click", ".addSoundcloudLink", function () {
    var $that = $(this);
    $.getJSON(soundCloudLinkUrl, function (json) {
        var container = $that.parent().parent().find('.input-container');
        container.append(json.text);

        $(".audio-input").find(":file").filestyle({
            buttonText: "",
            buttonName: "btn-primary",
            iconName: "fa fa-file-audio-o",
            buttonBefore: true,
            placeholder: "Keine Datei ausgewählt."
        });
    });
});
// endregion

// region addSlideshow functionality
function setUpDropzoneContainerForSlideshow() {
    $('.add-content-slideshow').last().find('form').dropzone({
        url: projectPostUrl,
        addRemoveLinks: true,
        dictDefaultMessage: "Hier klicken",
        dictRemoveFile: "Entfernen",
        acceptedFiles: 'image/*',
        // referring to https://github.com/enyo/dropzone/wiki/Combine-normal-form-with-Dropzone
        autoProcessQueue: false,
        uploadMultiple: true,
        parallelUploads: 100,
        maxFiles: 10,
        init: function () {
            this.on("error", function (file, errMsg, xhr) {
                if (!file.accepted) this.removeFile(file);
            });
        }
    });
}
// endregion

// region project socials
$('[id^=link]').find('.btn').on("click", function () {
    $(this).parent().hide();
    $(this).parent().next().removeClass("hidden");
});

$('.link-close').on("click", function () {
    $(this).parent().prev().show();
    $(this).parent().addClass("hidden");
    $(this).next().val("");
});
// endregion

// region modal crop
body_element.on("click", "#crop_button", function () {
    var $img = $('#title_image');
    var imgurl = $img.cropper('getCroppedCanvas').toDataURL();
    crop_data = JSON.stringify($img.cropper("getData"));
    $('#selectedImage').attr("src", imgurl).removeClass("hidden");
    $('#imgUploadModal').modal("toggle");
    $('#icon-upload-title-image').addClass("hidden");
});
// endregion
// ########################################

// ############## RIGHT PANE ##############
//region member, supervisor
function aMemberNameEmpty() {
    var result = false;
    $('.pu-member-select2').each(function () {
        if ($(this).val() === "") {
            result = true;
            return false;
        }
    });
    return result;
}

$('#pu-add-member').on("click", function () {
    if (!aMemberNameEmpty()) {
        $.getJSON(memberRespUrl, function (json) {
            member_wrapper.append(json.text);
            $(".pu-member-select2").select2({
                containerCss: "pu-member-select2",
                placeholder: "Mitglied wählen"
            });

            $(".resp-bar").tagit({
                placeholderText: 'Tätigkeit hinzufügen',
                autocomplete: {
                    source: [] //TODO: Get list of all tags from server
                },
                showAutocompleteOnFocus: true
            });
        });
    }
});

$('#pu-add-supervisor').on("click", function () {
    var $pre_last = $('.profs-choices').eq(-1);
    var selection = $pre_last.val();
    if ($pre_last.length == 0 || !(selection === "choose")) {
        $.getJSON(supervisorChoicesUrl, function (json) {
            supervisor_wrapper.append(json.text);
            $('.profs-choices').select2({
                containerCss: "prof-choices",
                placeholder: "Betreuer wählen"
            });
        });
    }
});
//endregion

// region degree select
$('#degreeprogram-select').change(function () {
    var id = $(this).val();
    $.ajax({
        url: "/subjects_by_degree_program/" + id,
        dataType: 'json',
        type: 'POST',
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN},
        success: function (data) {
            $('#subject-select').find('option').remove().end();
            $.each(data, function (i, item) {
                $('#subject-select').append($('<option>', {
                    value: item.id,
                    text: item.name
                }));
            });
            if (window.loadComplete) {
                if ($('#subject-preload').val()) {
                    $('#subject-select').val($('#subject-preload').val()).trigger("change");
                }
                if ($('#semesteryear-preload').val()) {
                    $('#semesteryear-select').val($('#semesteryear-preload').val()).trigger("change");
                }

                window.loadComplete = false;
            }
        },
        error: function (request, status, error) {
            console.log("Ajax Request Error - Status: " + status, " - Error: " + error);
        }
    });
});

//endregion
// ########################################

// region image read & cropper init
function readURL(input, img_selector) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            if (img_selector == "") {
                // modal handling
                $('#title_image').cropper('destroy');
                $('#title_image').removeClass("hidden").attr('src', e.target.result);
                $('.crop-menu').removeClass("hidden");
                $('.image_container').removeClass("hidden");
                $('#crop_button').prop("disabled", true);
                initCropper(16/9);
            } else {
                // reset preloaded data
                $(input).attr('data-existing-url', "");
                $(input).attr('data-original-name', "");
                // #addPicture handling
                var $img = $(input).parent().find(img_selector);
                $img.cropper('destroy');
                $img.siblings('input').val('');
                $img.removeClass("hidden").attr('src', e.target.result);
                $('.image_container').removeClass("hidden");
                $img.parent().find('.crop-menu').removeClass("hidden")
                    .find('.crop_button').prop("disabled", true);
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function initCropper(aspect_ratio) {
    $('#title_image').cropper({
        aspectRatio: aspect_ratio
    });
    $('#crop_button').prop("disabled", false);
}
//endregion

// region close
body_element.on("click", ".sub-content-close", function () {
    $(this).parent().remove();
});
//endregion

var charCount = function (text_max, input, span) {
    $(span).html(0 + '/' + text_max);
    $(input).keyup(function () {
        var text_length = $(input).val().length;
        $(span).html(text_length + '/' + text_max);
    });
};

// region initialize pre loaded
function initializePreLoadedContent() {
    $.each($(".video-input,.audio-input,.image-file-input").find(":file"), function (i, obj) {
        $(this).filestyle({
            buttonText: "",
            buttonName: "btn-primary",
            iconName: $(this).attr("data-icon"),
            buttonBefore: true,
            placeholder: $(this).attr('data-placeholder')
        });
    });

    $.each($('.add-content-slideshow'), function (i, slideshow_section) {
        var existing_images = [];
        $.each($(this).find('.slideshow-preload'), function (i, obj) {
            existing_images.push($(this).val());
        });
        console.log($(this));
        $(slideshow_section).find('form').dropzone({
            url: projectPostUrl,
            addRemoveLinks: true,
            dictDefaultMessage: "Hier klicken",
            dictRemoveFile: "Entfernen",
            acceptedFiles: 'image/*',
            // referring to https://github.com/enyo/dropzone/wiki/Combine-normal-form-with-Dropzone
            autoProcessQueue: false,
            uploadMultiple: true,
            parallelUploads: 100,
            maxFiles: 10,
            removedFiles : [],
            init: function () {
                this['removedFiles'] = [];

                this.on("error", function (file, errMsg, xhr) {
                    if (!file.accepted) this.removeFile(file);
                });

                var myDropzone = this;

                $.each(existing_images, function (i, obj) {
                    var mockFile = {
                        url: obj
                    };
                    console.log(mockFile.url);
                    myDropzone.emit("addedfile", mockFile);
                    myDropzone.createThumbnailFromUrl(mockFile, mockFile.url, null, null);
                    myDropzone.files.push(mockFile);
                    myDropzone.emit("complete", mockFile);
                });

                this.on("removedfile", function (file) {
                    console.log(file);
                    if ('url' in file) {
                        this.removedFiles.push(file);
                    }
                });
            }
        });
    });

    $('.resp-bar').tagit();

    $(".pu-member-select2").select2({
        containerCss: "pu-member-select2",
        placeholder: "Mitglied wählen"
    });

    $('.profs-choices').select2({
        containerCss: "prof-choices",
        placeholder: "Betreuer wählen"
    });
}
// enregion

// region ready(), addcontent, choices, tagit initalize
$(document).ready(function () {
    window.loadComplete = true;
    initializePreLoadedContent();

    $.getJSON(addContentChooseUrl, function (json) {
        addcontent = json.text;
    });

    $.getJSON(addContentChoicesUrl, function (json) {
        addcontentchoice = json.text;
    });

    $("#add-tags-bar").tagit({
        placeholderText: 'Hinzufügen',
        autocomplete: {
            source: [] //TODO: Get list of all tags from server
        },
        showAutocompleteOnFocus: true
    });

    $("#resp-bar-" + currentUser).tagit({
        placeholderText: 'Tätigkeit hinzufügen',
        autocomplete: {
            source: [] //TODO: Get list of all tags from server
        },
        showAutocompleteOnFocus: true
    });
    $('#degreeprogram-select').trigger('change');
});
//endregion