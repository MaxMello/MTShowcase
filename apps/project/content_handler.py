import json

from apps.project.forms import VideoFileField, AudioFileField, ImageFormField
from apps.project.image_crop import crop_image_and_save
from apps.project.models import Project, ProjectUploadContentFile
from apps.project.providers import EmbedProvider, Youtube, Vimeo, Soundcloud
from apps.project.validators import url_validator


class EmptyFileContentException(Exception):
    def __init__(self, section_index, content_index):
        super(EmptyFileContentException, self).__init__()
        self.section_index = section_index
        self.content_index = content_index


class ProjectJsonBuilder(object):
    def __init__(self, content_json, request, method, project):
        self.request = request
        self.method = method
        self.project = project
        self.content_json = content_json

    def build_project_json(self, uploader_instance):
        project_json_content = []
        section_content_list = self.content_json['content']
        print("start build ", section_content_list is not None)
        try:
            # for all content sections (add-content-areas)
            for section_index, key in enumerate(sorted(section_content_list)):
                current_section = {}
                content_section_obj = section_content_list[key]
                content_type = content_section_obj['content_type']
                visibility = content_section_obj['visibility']
                current_section['subheading'] = content_section_obj['subheading']
                current_section['content_type'] = content_type
                current_section['visibility'] = visibility
                current_section['contents'] = []

                # for single input-content inside each content section
                for content_index, content in enumerate(content_section_obj['content']):
                    try:
                        if content_type == Project.VIDEO:
                            print("Handle Video")
                            form_class = VideoFileField
                            embed_provider = EmbedProvider([Youtube(), Vimeo()])
                            created_content = self.__content_video_audio(content, content_type, form_class,
                                                                         embed_provider,
                                                                         section_index, content_index, visibility)
                            print("Video success")

                        elif content_type == Project.AUDIO:
                            form_class = AudioFileField
                            embed_provider = EmbedProvider([Soundcloud()])
                            created_content = self.__content_video_audio(content, content_type, form_class,
                                                                         embed_provider,
                                                                         section_index, content_index, visibility)

                        elif content_type == Project.IMAGE:
                            created_content = self.__content_image(content, content_type, section_index, content_index,
                                                                   visibility)

                        elif content_type == Project.SLIDESHOW:
                            created_content = self.__content_slideshow(content, content_type, visibility)

                        elif content_type == Project.TEXT:
                            created_content = self.__content_text(content, content_type)
                        else:
                            created_content = None

                        if created_content:
                            current_section['contents'].append(created_content)

                    except EmptyFileContentException as e:
                        print("Empty File Content")
                        uploader_instance.errors.append({
                            'section': e.section_index,
                            'input': e.content_index,
                            'error': "Der Datei-Input ist nicht korrekt. Füge einen hinzu oder entferne den Input!"
                        })
                        continue
                    except Exception as e:
                        print("Error handling: [" + content_type + "]: " + str(e))
                        # Ignore the content that causes an error and step one ahead
                        # trying to save the remaining content. This is done so that valid
                        # content is not lost on saving.
                        continue

                # end for content in section
                project_json_content.append(current_section)

            # end for section
            return project_json_content
        except Exception as e:
            print("Unexpected Content Error", str(e))

    def __content_text(self, content, content_type):
        return {
            'content_type': content_type,
            'text': content['text']
        }

    def __file_invalid(self, field, content, content_type, section_index, content_index):
        if self.method == 'save' and not field:
            return {
                "content_type": content_type,
                "filename": None,
                "original_name": None,
                "text": content['text']
            }
        elif self.method == 'publish':
            raise EmptyFileContentException(section_index, content_index)

    def __content_video_audio(self, content, content_type, form_class, embed_provider, section_index, content_index,
                              visibility):
        if 'filename' in content:
            if 'existing' in content['filename']:
                existing_data = content['filename']['existing']
                filename = existing_data['url']
                existing_file = ProjectUploadContentFile.objects.filter(project=self.project, file=filename).first()
                if not existing_file:
                    # Existing file is not owned by project, that is a critical error
                    # so stop here for this content
                    raise Exception()
                # retrieved file update content visibility to new
                existing_file.visible = visibility
                existing_file.save()

                original_name = existing_data['original_name']
                return {
                    "content_type": content_type,
                    "filename": existing_file.file.name,
                    "original_name": original_name,
                    "text": content['text']
                }
            else:
                field = content['filename']
                form = form_class(field, self.request.POST, self.request.FILES)
                if form.is_valid():
                    original_name = form.cleaned_data[field].name
                    saved_file = ProjectUploadContentFile.objects.create(
                        project=self.project, file=form.cleaned_data[field], visible=visibility)
                    if saved_file is not None:
                        try:
                            return {
                                "content_type": content_type,
                                "filename": saved_file.file.name,
                                "original_name": original_name,
                                "text": content['text']
                            }
                        except KeyError as e:
                            print("error while video labels" + str(e))
                else:
                    self.__file_invalid(field, content, content_type, section_index, content_index)

        elif 'url' in content:
            result = embed_provider.get_iframe(content['url'])
            if result:
                iframe, media_host = result
                return {
                    "content_type": content_type,
                    "media_host": media_host,
                    "url": content['url'],
                    "i_frame": iframe,
                    "text": content['text']
                }

    def __content_slideshow(self, content, content_type, visibility):
        image_urls = []
        for filename in content['existing']:
            existing_file = ProjectUploadContentFile.objects.filter(project=self.project, file=filename).first()
            if not existing_file:
                raise Exception("Slideshow File not owned by Project")
            existing_file.visible = visibility
            existing_file.save()

            image_urls.append(existing_file.file.name)

        for field_name in content['slideshow']:
            form = ImageFormField(field_name, self.request.POST, self.request.FILES)
            if form.is_valid():
                saved_file = ProjectUploadContentFile.objects.create(
                    project=self.project, file=form.cleaned_data[field_name], visible=visibility
                )
                if saved_file is not None:
                    image_urls.append(saved_file.file.name)
            else:
                print(form.errors)

        if image_urls:
            return {
                'content_type': content_type,
                'images': image_urls
            }

    def __content_image(self, content, content_type, section_index, content_index, visibility):
        if 'filename' in content:
            crop_data = None
            saved_file = None

            if 'crop_data' in content:
                try:
                    crop_data = json.loads(content['crop_data'])
                except Exception as e:
                    print("No Crop Data supplied or error")

            if 'existing' in content['filename']:
                existing_data = content['filename']['existing']
                filename = existing_data['url']
                original_name = existing_data['original_name']

                existing_image = ProjectUploadContentFile.objects.filter(
                    project=self.project, file=filename
                ).first()
                if existing_image:
                    existing_image.visible = visibility
                    existing_image.save()
                    if crop_data:
                        path = existing_image.file.path
                        saved_file = crop_image_and_save(self.project, path, crop_data, visibility)
                        # delete old image from storage
                        ProjectUploadContentFile.objects.get(project=self.project, file=filename).file.delete()

                return {
                    "content_type": content_type,
                    "filename": saved_file.file.name if saved_file else existing_image.file.name,
                    "original_name": original_name,
                    "text": content['text']
                }

            else:
                field_name = content['filename']
                form = ImageFormField(field_name, self.request.POST, self.request.FILES)
                if form.is_valid():
                    original_name = form.cleaned_data[field_name].name
                    if crop_data:
                        saved_file = crop_image_and_save(self.project, form.cleaned_data[field_name], crop_data, visibility)
                    else:
                        saved_file = ProjectUploadContentFile.objects.create(
                            project=self.project, file=form.cleaned_data[field_name], visible=visibility
                        )

                    return {
                        "content_type": content_type,
                        "filename": saved_file.file.name,
                        "original_name": original_name,
                        "text": content['text']
                    }
                else:
                    self.__file_invalid(field_name, content, content_type, section_index, content_index)

        elif 'url' in content:
            try:
                url_validator(content['url'])
                return {
                    "content_type": content_type,
                    "url": content['url'],
                    "text": content['text']
                }
            except:
                pass
