from apps.project.models import Project, ProjectUploadContentFile


def clear_removed_files(project, old_project_content, new_project_content):
    old_files = extract_file_paths_from_json(old_project_content)
    new_files = extract_file_paths_from_json(new_project_content)

    try:
        for filename in old_files:
            if filename not in new_files:
                print("##############################################")
                print("About to delete: " + filename)
                obj = ProjectUploadContentFile.objects.filter(project=project, file=filename).first()
                if obj:
                    obj.file.delete(False)
                    obj.delete()
    except Exception as e:
        print("Error during ClearFiles: " + str(e))


def extract_file_paths_from_json(json_content):
    files = []
    try:
        for section in json_content:
            for content in section['contents']:
                if content['content_type'] == Project.IMAGE and 'filename' in content:
                    files.append(content['filename'])

                elif content['content_type'] == Project.AUDIO and 'filename' in content:
                    files.append(content['filename'])

                elif content['content_type'] == Project.VIDEO and 'filename' in content:
                    files.append(content['filename'])

                elif content['content_type'] == Project.SLIDESHOW and 'images' in content:
                    for filename in content['images']:
                        files.append(filename)
    except:
        print("PATH FROM JSON: ", files)
        return files
    else:
        return files
