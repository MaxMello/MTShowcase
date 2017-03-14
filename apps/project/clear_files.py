from apps.project.models import Project, UploadImage, UploadAudio, UploadVideo


def clear_removed_files(old_project_content, new_project_content):
    old_images, old_audios, old_videos = extract_file_paths_from_json(old_project_content)
    new_images, new_audios, new_videos = extract_file_paths_from_json(new_project_content)

    delete_files(old_images, new_images, UploadImage)
    delete_files(old_audios, new_audios, UploadAudio)
    delete_files(old_videos, new_videos, UploadVideo)


def delete_files(old_files, new_files, model_cls):
    try:
        for file in old_files:
            if file not in new_files:
                print("##############################################")
                print("About to delete: " + file)
                obj = model_cls.objects.filter(file=file.replace("/media/", "")).first()
                if obj:
                    obj.file.delete()
                    obj.delete()
    except:
        pass


def extract_file_paths_from_json(json_content):
    images = []
    audios = []
    videos = []
    try:
        for section in json_content:
            for content in section['contents']:
                if content['content_type'] == Project.IMAGE and 'filename' in content:
                    images.append(content['filename'])

                elif content['content_type'] == Project.AUDIO and 'filename' in content:
                    audios.append(content['filename'])

                elif content['content_type'] == Project.VIDEO and 'filename' in content:
                    videos.append(content['filename'])

                elif content['content_type'] == Project.SLIDESHOW and 'images' in content:
                    for filename in content['images']:
                        images.append(filename)
    except:
        print("PATH FROM JSON: ", images, audios, videos)
        return images, audios, videos
    else:
        return images, audios, videos