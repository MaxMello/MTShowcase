import datetime
import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy

from apps.project.content_handler import ProjectJsonBuilder
from apps.project.forms import ImageFormField
from apps.project.image_crop import crop_compress_save_title_image
from apps.project.models import DegreeProgram, Subject, Project, ProjectSocial, Tag, ProjectTag, ProjectMember, \
    ProjectMemberResponsibility, ProjectSupervisor, ProjectEditor
from apps.project.validators import validate_empty, UrlToSocialMapper
from apps.user.models import User


class UploaderInitializationException(Exception):
    pass


class EmptyValueException(Exception):
    pass


class UnsupportedJsonFormatException(Exception):
    pass


class Uploader(object):
    def __init__(self, request):
        try:
            self.request = request
            self.project = None
            self.cleaned_data = {}
            self.request_json = json.loads(request.POST.get('params'))
            self.__validate_format_and_types(self.request_json)
            self.method = self.request_json['upload_method']
            self.errors = []

            self.__start()
        except UnsupportedJsonFormatException:
            print("Init Format Exception")
            raise UploaderInitializationException()
        except Exception as e:
            print("Init Upload Exception: " + str(e))
            raise UploaderInitializationException()

    def __start(self):
        try:
            self.__clean_heading()
            self.__clean_subheading()
            self.__clean_description()
            self.__clean_supervisor()
            self.__clean_degree_program()
            self.__clean_subject()
            self.__clean_members()
            self.__clean_tags()
            self.__clean_semester_year()
        except Exception as e:
            print("Error cleaning " + str(e))

        print("########## Clean successful")

        if self.is_valid():
            print("########## Upload was valid")
            # 1: Create or update Project from post-data
            self.__get_or_create_project()
            if self.project:
                # 2: Add cross table relations
                ProjectEditor.objects.get_or_create(project=self.project, editor=self.request.user.get_lib_user())
                self.__insert_socials()
                self.__insert_tags()
                self.__insert_members()
                self.__insert_supervisors()

                print("-Relations inserted")

                try:
                    # 3: Add project title image and cropped image for home grid
                    self.__crop_title_images()
                    print("-Title images cropped")

                    # 4: Try to build variable project content from request json
                    old_project_json = self.project.contents
                    builder = ProjectJsonBuilder(self.request_json['p_contents'], self.request, self.method,
                                                 self.project)
                    print("-Created JsonBuilder")
                    project_content_json = builder.build_project_json(self)
                    self.project.contents = project_content_json
                    print("-Project Content build")
                    print(self.project.contents)

                    self.project.save()

                    # 5: If in publish set state for professor review and send notification mail
                    if self.__in_publish_mode():
                        self.project.send_prof_notification()

                    # 6: Remove files that are not used any more in this version of the project
                    # to clear storage space
                    if old_project_json is not None:
                        print("CLEAR FILES")
                        from .clear_files import clear_removed_files
                        clear_removed_files(self.project, old_project_json, project_content_json)

                except Exception as e:
                    print("Error building JSON " + str(e))

            else:
                raise Exception()

    def is_valid(self):
        return len(self.errors) == 0

    def response_data(self):
        response = {}
        if self.__in_publish_mode():
            response = {'redirect': str(reverse_lazy('home'))}
        elif self.__in_save_mode():
            redirect_url = reverse_lazy('edit-project', kwargs={'base64_unique_id': self.project.unique_id_base64()})
            response = {'save_success': True, 'redirect': str(redirect_url)}

        return self.errors[0] if len(self.errors) > 0 else response

    def __in_save_mode(self):
        return self.method == 'save'

    def __in_publish_mode(self):
        return self.method == 'publish'

    def __crop_title_images(self):
        if self.request.FILES:
            form = ImageFormField("title_image", self.request.POST, self.request.FILES)
            if form.is_valid():
                print("cleaned: ", form.cleaned_data["title_image"])
                self.project.project_image = self.request.FILES["title_image"]
                self.project.save()
                crop_compress_save_title_image(
                    project_object=self.project,
                    original=form.cleaned_data["title_image"],
                    crop_data=self.title_image_crop_data
                )

    def __insert_socials(self):
        ProjectSocial.objects.filter(project=self.project).delete()

        for social_url in self.request_json['p_project_links']:
            social = UrlToSocialMapper.return_social_from_url_or_none(social_url)
            if social:
                ProjectSocial.objects.get_or_create(project=self.project, social=social, url=social_url)

    def __insert_tags(self):
        ProjectTag.objects.filter(project=self.project).delete()

        for tag in self.cleaned_data['project_tags']:
            new_tag, created = Tag.objects.get_or_create(value=tag)
            ProjectTag.objects.get_or_create(project=self.project, tag=new_tag)

    def __insert_members(self):
        for (index, key) in enumerate(self.cleaned_data['member_responsibilities']):
            tags = self.cleaned_data['member_responsibilities'][key]
            user = User.objects.filter(pk=key).first()
            member, created = ProjectMember.objects.get_or_create(member=user, project=self.project)
            for tag in tags:
                new_tag, created = Tag.objects.get_or_create(value=tag)
                ProjectMemberResponsibility.objects.get_or_create(
                    project_member=member,
                    responsibility=new_tag,
                    position=index
                )

    def __insert_supervisors(self):
        for supervisor in self.cleaned_data['supervisors']:
            ProjectSupervisor.objects.get_or_create(project=self.project, supervisor=supervisor)

    def __get_or_create_project(self):
        try:
            project_id = None
            if self.request.POST and 'project_unique_id' in self.request.POST:
                print("########## GOT EXISTING #+++++++++++++++++")
                project_unique_id = Project.base64_to_uuid(self.request.POST.get("project_unique_id"))
                existing_project = Project.objects.filter(unique_id=project_unique_id).first()
                if existing_project:
                    project_id = existing_project.id

            project, created = Project.objects.update_or_create(
                pk=project_id,
                defaults={
                    'heading': self.cleaned_data['heading'],
                    'subheading': self.cleaned_data['subheading'],
                    'description': self.cleaned_data['description'],
                    'semester': self.cleaned_data['semester'],
                    'year_from': self.cleaned_data['year_from'],
                    'year_to': self.cleaned_data['year_to'],
                    'degree_program': self.cleaned_data['degree_program'],
                    'subject': self.cleaned_data['subject']
                }
            )
            if created:
                print("-Created Project")
            else:
                print("-Updated Project")
            self.project = project
        except Exception as e:
            print(str(e))

            self.project = None

    def __clean_semester_year(self):
        try:
            semesteryear = self.request_json['p_semesteryear']
            semester = semesteryear[:2]
            if not semester or semester not in [Project.WINTER, Project.SUMMER]:
                raise Exception("Semester was wrong")
            year_from = semesteryear[2:]
            year_choices = reversed([r for r in range(1980, datetime.date.today().year + 1)])
            if not year_from or int(year_from) not in year_choices:
                raise Exception("Year From was wrong")
            year_to = int(year_from) + 1 if semester == Project.WINTER else year_from

            self.cleaned_data['semester'] = semester
            self.cleaned_data['year_from'] = year_from
            self.cleaned_data['year_to'] = year_to
            print("Cleaned SemesterYear")
        except Exception as e:
            print(str(e))
            self.errors.append({'id': "", 'error': "Das Semester ist nicht korrekt."})

    def __clean_degree_program(self):
        try:
            degree_program_id = self.request_json['p_degree_program']
            degree_program = DegreeProgram.objects.get(pk=degree_program_id)
            self.cleaned_data['degree_program'] = degree_program
            print("Cleaned DegreeProgram")
        except ObjectDoesNotExist:
            self.errors.append({'id': "", 'error': "Der gewählte Studiengang existiert nicht."})

    def __clean_subject(self):
        try:
            subject_id = self.request_json['p_subject']
            subject = Subject.objects.get(pk=subject_id)
            self.cleaned_data['subject'] = subject
            print("Cleaned Subject")
        except ObjectDoesNotExist:
            self.errors.append({'id': "", 'error': "Die gewählte Vorlesung existiert nicht."})

    def __clean_heading(self):
        try:
            heading = validate_empty(self.request_json['p_heading'])
            if not heading and not self.__in_save_mode():
                raise Exception()
            self.cleaned_data['heading'] = heading
            print("Cleaned Heading")
        except:
            self.errors.append({'id': "heading", 'error': "Der Titel darf nicht leer sein"})

    def __clean_subheading(self):
        try:
            subheading = validate_empty(self.request_json['p_subheading'])
            if not subheading and not self.__in_save_mode():
                raise Exception()
            self.cleaned_data['subheading'] = subheading
            print("Cleaned Subheading")
        except:
            print("got error")
            self.errors.append({'id': "subheading", 'error': "Der Untertitel darf nicht leer sein"})

    def __clean_description(self):
        try:
            description = validate_empty(self.request_json['p_description'])
            if not description and not self.__in_save_mode():
                raise Exception()
            self.cleaned_data['description'] = description
            print("Cleaned Description")
        except:
            self.errors.append({'id': "description", 'error': "Der Beschreibung darf nicht leer sein"})

    def __clean_tags(self):
        self.cleaned_data['project_tags'] = self.request_json['p_project_tags']
        print("Cleaned Tags")

    def __clean_members(self):
        member_resp_dict = self.request_json['p_member_responsibilities']
        if '' in member_resp_dict:
            del member_resp_dict['']
        self.cleaned_data['member_responsibilities'] = member_resp_dict
        print("Cleaned Members")

    def __clean_supervisor(self):
        try:
            supervisors = self.request_json['p_supervisors']
            if not supervisors and not self.__in_save_mode():
                raise Exception()

            # TODO: define if student/admin can be supervisor
            cleaned_supervisors = []
            all_supervisors = User.objects.filter(type=User.PROF)
            for supervisor_id in self.request_json['p_supervisors']:
                supervisor = User.objects.filter(pk=supervisor_id).first()
                if supervisor is None or supervisor not in all_supervisors:
                    raise Exception()
                cleaned_supervisors.append(supervisor)

            self.cleaned_data['supervisors'] = cleaned_supervisors
            print("Cleaned Supervisors")
        except:
            self.errors.append({'id': "upload-top-right", 'error': "Jedes Projekt braucht einen Betreuer!"})

    def __validate_format_and_types(self, request_json):
        try:
            print(request_json)
            method = request_json['upload_method']
            if not isinstance(method, str) or method not in ['save', 'publish']:
                raise Exception("Method was wrong")

            str_test_lists = [
                [request_json['p_heading'],
                 request_json['p_subheading'],
                 request_json['p_description'],
                 request_json['p_semesteryear']],

                request_json['p_project_tags'],

                request_json['p_project_links']
            ]

            for entry_list in str_test_lists:
                for item in entry_list:
                    if not isinstance(item, str):
                        raise Exception("Str lists were wrong")

            degree_program_id = request_json['p_degree_program']
            int(degree_program_id)

            subject_id = request_json['p_subject']
            int(subject_id)

            supervisors_list = request_json['p_supervisors']
            for supervisor_id in supervisors_list:
                int(supervisor_id)

            member_resp_list = request_json['p_member_responsibilities']
            non_empty_keys = {key for key in member_resp_list.keys() if key and key.isdigit()}
            if not non_empty_keys:
                raise Exception("Member resp were empty")
            for key in non_empty_keys:
                for resp in member_resp_list[key]:
                    if not isinstance(resp, str):
                        raise Exception("Member resp value wrong")

            project_contents = request_json['p_contents']

            self.title_image_crop_data = \
                json.loads(self.request.POST['crop_data']) if 'crop_data' in self.request.POST else None

            print("Validate FormatTypes success")
        except Exception as e:
            print("Validate FormatTypes failure: ", str(e))
            raise UnsupportedJsonFormatException()
