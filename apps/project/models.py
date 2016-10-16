import datetime
import json

import re
from apps.project import stopwords
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from MTShowcase.settings import STATIC_URL, MEDIA_URL
from apps.user.models import User
from django.db.models import Count


def can_be_supversivor(value):
    print(value)
    user = User.objects.filter(id=value).first()
    print(user)
    if not (user.type == User.ADMIN or user == User.PROF):
        raise ValidationError(message="{} is not a user applicable for being a supervisor".format(value))


def project_directory_path(instance, filename):
    return 'project_{0}/title_image/{1}'.format(instance.id, filename)


class Project(models.Model):
    SUMMER = 'SS'
    WINTER = 'WS'

    SEMESTER = (
        (SUMMER, 'Summer semester'),
        (WINTER, 'Winter semester'),
    )

    EDIT_STATE = 'EDITABLE'
    REVIEW_STATE = 'FOR_REVIEW'
    REVISION_STATE = 'FOR_REVISION'
    APPROVED_STATE = 'APPROVED'

    APPROVAL_STATES = (
        (EDIT_STATE, 'For users to edit'),
        (REVIEW_STATE, 'For supervisors to review'),
        (REVISION_STATE, 'For users to improve'),
        (APPROVED_STATE, 'Publicly viewable')
    )

    YEAR_CHOICES = [(r, r) for r in range(1980, datetime.date.today().year + 1)]

    # DISPLAYED CONTENT
    project_image = models.ImageField(upload_to=project_directory_path, default=STATIC_URL + 'images/default_project_image.jpg')
    project_image_cropped = models.ImageField(upload_to=project_directory_path, default=STATIC_URL + 'images/default_project_image.jpg')
    heading = models.CharField(max_length=100)
    subheading = models.CharField(max_length=255)
    description = models.TextField(max_length=2000)
    tags = models.ManyToManyField('Tag', through='ProjectTag', through_fields=('project', 'tag'),
                                  related_name='project_tag')

    # PROJECT INFO
    semester = models.CharField(max_length=2, choices=SEMESTER, default=SUMMER)
    year_from = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    year_to = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    degree_program = models.ForeignKey('DegreeProgram', on_delete=models.PROTECT)
    subject = models.ForeignKey('Subject', on_delete=models.PROTECT)
    socials = models.ManyToManyField('user.Social', through='ProjectSocial', through_fields=('project', 'social'),
                                     related_name='project_social')

    # ASSOCIATED USERS
    members = models.ManyToManyField('user.User', through='ProjectMember', through_fields=('project', 'member'),
                                     related_name='project_member')
    supervisors = models.ManyToManyField('user.User', through='ProjectSupervisor', through_fields=('project', 'supervisor'),
                                         related_name='project_supervisor')

    # META DATA
    views = models.IntegerField(default=0)
    upload_date = models.DateTimeField(auto_now_add=True)
    approval_state = models.CharField(max_length=20, choices=APPROVAL_STATES, default=EDIT_STATE)
    search_string = models.TextField(max_length=5000, default="-")

    def __str__(self):
        return 'ID: {} - {} - {} - Status: {} - {} views (Hochgeladen {})'.format(self.id, self.heading, self.get_semester_year_string(),
                                                                                  self.approval_state, self.views, self.upload_date)

    def get_title_image_path(self):
        return "{0}{1}{2}".format(STATIC_URL, "project/images/", self.title_image)

    def get_all_content(self):
        return ProjectContent.objects.filter(project=self).order_by('position')

    def get_all_content_json(self):
        jsons = [dict(json.loads(content.content), **{'content_type': content.content_type, 'content_path': content.project_content_directory_path()})
                 for content
                 in ProjectContent.objects.filter(project=self).order_by('position')]
        print(jsons)
        return jsons

    def get_semester_year_string(self):
        if self.semester == self.SUMMER:
            return "SoSe" + " " + str(self.year_from)
        elif self.semester == self.WINTER:
            return "WiSe" + " " + str(self.year_from) + "/" + str(self.year_to)

    def get_date_string(self):
        return self.upload_date.date().strftime("%d.%m.%Y")

    def build_search_string(self):
        print("BUILD SEARCH STRING")
        pattern = re.compile(stopwords.punctuation_regex)

        search_string = ''
        search_string += ' ' + pattern.sub(' ', str(self.heading))
        search_string += ' ' + pattern.sub(' ', str(self.subheading))
        search_string += ' ' + stopwords.remove_stoppwords(self.description)
        for content in self.get_all_content():
            content_json = json.loads(content.content)
            if content_json is not None:
                if 'subheading' in content_json:
                    search_string += ' ' + stopwords.remove_stoppwords(content_json['subheading'])
                if 'text' in content_json:
                    search_string += ' ' + pattern.sub(' ', content_json["text"])
        search_string += ' Sommersemester ss sose sommer semester summersemester summer semester' if self.semester == self.SUMMER else \
            ' Wintersemester ws wise winter semester'
        search_string += ' ' + self.get_semester_year_string()
        search_string += ' ' + str(self.year_from) + ' ' + str(self.year_to)

        # We cannot remove duplicate words, because we allow whitespaces in search words. Example:
        # Tag = "White Rabbit"
        # search_string = "Blue White Red [White] Rabbit"
        # The 2. white would get removed, so we would not find "White Rabbit"
        return search_string

    def save(self, *args, **kwargs):
        if self.id is not None:
            orig = Project.objects.get(id=self.id)
            print(orig)
            if orig.tags != self.tags or orig.heading != self.heading or orig.subheading != self.subheading or orig.description != self.description \
                    or orig.semester != self.semester or orig.year_from != self.year_from or orig.year_to != self.year_to \
                    or orig.search_string != self.search_string:
                self.search_string = self.build_search_string()
        else:
            self.search_string = self.build_search_string()
        super(Project, self).save(*args, **kwargs)

    def update_search_string(self):
        self.search_string = self.build_search_string()
        super(Project, self).save()


class ProjectContent(models.Model):
    # CHOICES
    TEXT = 'TEXT'
    IMAGE = 'IMAGE'
    SLIDESHOW = 'SLIDESHOW'
    VIDEO = 'VIDEO'
    AUDIO = 'AUDIO'

    CONTENT_TYPE = (
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
        (SLIDESHOW, 'Slideshow'),
        (VIDEO, 'Video'),
        (AUDIO, 'Audio')
    )

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    position = models.IntegerField(default=0)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE, default=TEXT)
    content = models.TextField(max_length=2000, default='{"subheading": "", "text": ""}')
    """
    Content Documentation:
     - Content is a JSON
     - content_type = TEXT:
        - subheading: Überschrift für den Abschnitt
        - text: Text inkl. einiger Styling-Elemente (Fett) #TODO: Vielleicht markup/nicht html?
     - content_type = IMAGE:
        - text: Text unter dem Bild
        - ref_type = INTERNAL | EXTERNAL
            - ref_type = INTERNAL:
                - filename: Name der Datei
            - ref_type = EXTERNAL:
                - url: Link zum Bild
     - content_type = SLIDESHOW:
        - images: ordered list of IMAGE-Jsons (see above)
     - content_type = VIDEO:
        - text: Text unter dem Video
        - ref_type: (see above)
            - ref_type = EXTERNAL:
                + media_host: Website/Source des Videos (YouTube, Vimeo, ...)
     - content_type = AUDIO:
        - text: Text unter dem Audioplayer
        - ref_type: (see above, video)
    """

    def __str__(self):
        return 'ID: {} - {} (ID: {}) - Typ {} - an Position {}:  {}'.format(self.id, self.project.heading, self.project.id, self.content_type,
                                                                            self.position, self.content)

    def project_content_directory_path(self):
        return MEDIA_URL + 'project_{0}/content_{1}/'.format(self.project.id, self.id)  # + Filename

    def save(self, *args, **kwargs):
        super(ProjectContent, self).save(*args, **kwargs)
        self.project.update_search_string()


class Tag(models.Model):
    value = models.CharField(max_length=50)

    def __str__(self):
        return "ID: {} - {}".format(self.id, self.value)

    def as_json(self):
        return dict(label=self.value)

    def mod10(self):
        return self.id % 10 + 1


class DegreeProgram(models.Model):
    BACHELOR = 'BACHELOR'
    MASTER = 'MASTER'

    ACADEMIC_DEGREE = (
        (BACHELOR, 'Bachelor'),
        (MASTER, 'Master'),
    )

    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=10)
    academic_degree = models.CharField(max_length=10, choices=ACADEMIC_DEGREE, default=BACHELOR)  # TODO: Add to search

    def __str__(self):
        return "ID: {} - {} ({}) - {} - {}".format(self.id, self.name, self.abbreviation, self.academic_degree, self.department.name)


class Subject(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    degree_programs = models.ManyToManyField(DegreeProgram)

    def __str__(self):
        return "ID: {} - {} ({}))".format(self.id, self.name, self.abbreviation)


class ProjectMember(models.Model):
    member = models.ForeignKey('user.User', on_delete=models.PROTECT)
    project = models.ForeignKey('Project', on_delete=models.PROTECT)
    display_username = models.BooleanField(default=True)
    responsibilities = models.ManyToManyField('Tag', through='ProjectMemberResponsibility',
                                              through_fields=('project_member', 'responsibility'),
                                              related_name='member_responsibility')

    def get_responsibilities(self):
        return [r.responsibility.value for r in ProjectMemberResponsibility.objects.filter(project_member=self).order_by('position').order_by('id')]

    def __str__(self):
        return "{} (ID: {}) - {} (ID: {}, {})".format(self.project.heading, self.project.id, self.member.unique_name, self.member.id,
                                                      "Sichtbar" if self.display_username else "Versteckt")


class ProjectSupervisor(models.Model):
    supervisor = models.ForeignKey('user.User', on_delete=models.PROTECT, validators=[can_be_supversivor])
    project = models.ForeignKey('Project', on_delete=models.PROTECT)

    def __str__(self):
        return "{} (ID: {}) - {} (ID: {})".format(self.project.heading, self.project.id, self.supervisor.unique_name, self.supervisor.id)


class ProjectTag(models.Model):
    project = models.ForeignKey('Project', on_delete=models.PROTECT)
    tag = models.ForeignKey('Tag', on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return "{} (ID: {}) - {} (ID: {})".format(self.project.heading, self.project.id, self.tag.value, self.tag.id)


class ProjectMemberResponsibility(models.Model):
    project_member = models.ForeignKey('ProjectMember', on_delete=models.CASCADE)
    responsibility = models.ForeignKey('Tag', on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField(default=1)  # TODO: Automatically order by default by occurrence

    def __str__(self):
        return "{} (ID: {}) - {} (ID: {}) : {}".format(self.project_member.project.heading, self.project_member.project.id,
                                                       self.project_member.member.unique_name, self.project_member.member.id,
                                                       self.responsibility.value)

    @staticmethod
    def get_skills_for_user(user):
        a = ProjectMemberResponsibility.objects.filter(project_member__member=user).values('responsibility__value').annotate(
            c=Count('responsibility__value')).order_by('-c')[:10]
        print(str(a))
        return a


class ProjectSocial(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    social = models.ForeignKey('user.Social', on_delete=models.CASCADE)
    url = models.URLField()
    description = models.CharField(max_length=30, default="")

    def __str__(self):
        return "{} (ID: {}) - {} (ID: {}): {}".format(self.project.heading, self.project.id, self.social.display_name, self.social.id, self.url)


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember


class ProjectSupervisorInline(admin.TabularInline):
    model = ProjectSupervisor


class ProjectTagInline(admin.TabularInline):
    model = ProjectTag


class ProjectAdmin(admin.ModelAdmin):
    inlines = (ProjectMemberInline, ProjectSupervisorInline, ProjectTagInline)