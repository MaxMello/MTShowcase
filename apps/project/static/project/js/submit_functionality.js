/**
 * Created by dirk on 09.03.2017.
 */

function getProjectLinks() {
    var p_links = [];
    $(".psocial input").each(function () {
        p_links.push($(this).val());
    });
    return p_links;
}

function getSupervisors() {
    var supervisors = [];
    $('.profs-choices').each(function (index, item) {
        if (item.value != "choose") {
            supervisors.push(item.value);
        }
    });
    return supervisors
}

function getMemberResponsibilities() {
    var users_responsibilities = {};
    var resp_arr = $('.resp-bar');
    $('.pu-member-select2').each(function (index, item) {
        users_responsibilities[$(this).val()] = $(resp_arr.get(index)).tagit("assignedTags");
    });
    users_responsibilities["" + currentUser] = $("#resp-bar-" + currentUser).tagit("assignedTags");
    return users_responsibilities;
}

function buildProjectContent(formData) {
    var $section = $('.upload-content-section');
    var content_json = {};

    // für jede Section (Content-Area + Subheading)
    $($section).each(function (section_index, obj) {
        content_json[section_index] = {};
        content_json[section_index]["content_type"] = $(this).attr('data-content-type');
        content_json[section_index]["subheading"] = $(this).find('.content-subheading').val();
        content_json[section_index]["content"] = [];

        $($(this).find('.input-container').children()).each(function (content_index, input_container) {
            // loop through all "content-input" (file, text, ...) inside the container
            var toAdd = {};
            $($(this).find('.content-input')).each(function (j, obj) {
                var key = $(this).attr('data-type-key');
                var value;
                if (key == 'filename') {
                    // build unique filename to find it during backend validation
                    var file_unique_name = section_index + $(this).attr('data-file-prefix') + "[" + content_index + "]";
                    formData.append(file_unique_name, obj.files[0]);
                    value = file_unique_name;

                } else if (key == 'slideshow') {
                    var slideshow_content_list = [];
                    var $dropZone = $(this);
                    if ($dropZone[0].dropzone.files.length > 0) {
                        $.each($dropZone[0].dropzone.files, function (i, obj) {
                            var fieldName = section_index + "file[" + i + "]";
                            formData.append(fieldName, obj);
                            slideshow_content_list.push(fieldName);
                        });
                    }
                    value = slideshow_content_list;
                }
                else {
                    value = $(this).val();
                }
                toAdd[key] = value;
            });
            content_json[section_index]["content"].push(toAdd);
        });
    });
    return {content: content_json};
}

$('#pu-publish').on("click", function () {
    var formData = new FormData();

    if ($('#image')[0].files.length > 0) {
        formData.append("title_image", $('#image')[0].files[0]);
        if (crop_data != null) {
            formData.append("crop_data", crop_data);
        }
    }

    var project_json_dict = JSON.stringify({
        p_heading: $('#heading').val(),
        p_subheading: $('#subheading').val(),
        p_description: $('#description').val(),
        p_degree_program: $('#degreeprogram-select').val(),
        p_semesteryear: $('#semesteryear-select').val(),
        p_subject: $('#subject-select').val(),
        p_supervisors: getSupervisors(),
        p_member_responsibilities: getMemberResponsibilities(),
        p_project_tags: $("#add-tags-bar").tagit("assignedTags"),
        p_project_links: getProjectLinks(),
        p_contents: buildProjectContent(formData)
    });
    formData.append("csrfmiddlewaretoken", window.CSRF_TOKEN);
    formData.append("params", project_json_dict);

    $.ajax({
        url: projectPostUrl,
        type: "POST",
        contentType: false,
        processData: false,
        data: formData,
        success: function (json) {
            alert("success");
        }
    });
});