from apps.project.models import Project, ProjectMember, ProjectMemberResponsibility
from django.db.models import Q


class Search:

    def __init__(self, user=None, tags=[], except_projects=[], order='default', maximum=50):
        #Input
        self.user_id = user if isinstance(user, int) else None
        self.tags = tags
        self.except_projects = except_projects
        self.order = order
        self.maximum = maximum if isinstance(maximum, int) else 50
        #Output
        self.projects = self.get_projects()
        self.projects_jsons = self.build_projects_jsons(self.maximum)

    """
    CREATE JSON
    """

    def build_projects_jsons(self, maximum):
        projects_jsons = []
        for index, proj in enumerate(self.projects):
            project_dict = {'id': proj.unique_id_base64(), 'img': proj.project_image.url, 'heading': proj.heading, 'order': index,
                       'search_string': self.build_frontend_search_string(proj),
                       'tags': {'prio1': self.tags_prio1(proj), 'prio2': self.tags_prio2(proj), 'prio3': self.tags_prio3(proj)}}
            projects_jsons.append(project_dict)
        return projects_jsons

    def build_frontend_search_string(self, project):
        search_string = project.search_string
        for p in project.tags.all():
            search_string += ' ' + str(p.value)
        search_string += ' ' + project.subject.name + ' ' + project.subject.abbreviation + ' ' + project.degree_program.name + ' ' \
                         + project.degree_program.abbreviation
        for m in project.members.all():
            search_string += ' ' + m.get_public_name()
            for pm in ProjectMember.objects.filter(member=m):
                for r in pm.responsibilities.all():
                    search_string += ' ' + r.value

        for m in project.supervisors.all():
            search_string += ' ' + m.get_public_name()
        return search_string

    def tags_prio1(self, project):
        prio1 = list([p['value'] for p in project.tags.values('value').all()])
        prio1 += list([p.get('responsibility__value') for p in ProjectMemberResponsibility.objects.filter(project_member__project=project).values('responsibility__value').all()])
        return prio1

    def tags_prio2(self, project):
        return [project.subject.name, project.degree_program.name, project.get_semester_year_string()]

    def tags_prio3(self, project):
        prio3 = []
        prio3 += list([m.get_public_name() for m in project.members.all()])
        prio3 += list([m.get_public_name() for m in project.supervisors.all()])
        return prio3

    """
    SEARCH PROJECTS
    """

    def get_projects(self):

        qset = Project.objects.filter(approval_state=Project.APPROVED_STATE)
        #print(qset)
        if not qset:
            return []

        if self.user_id:
            qset = qset.filter(members__id=self.user_id)
            if not qset:
                return []

        if self.except_projects:
            qset = qset.exclude(id__in=self.except_projects)
            if not qset:
                return []

        if self.tags:
            # TODO: FILTER BY FIRSTNAME + LASTNAME IF SHOW_CLEAR_NAME = TRUE
            #qset = qset.extra(select={'full_name':'select CONCAT(CONCAT(first_name, " "), last_name) from registration.AuthEmailUser where registration.AuthEmailUser.id = lib.user.auth_user'})
            qset = qset.filter(self.filter_for_tags(self.tags))
            if not qset:
                return []

        if self.order == 'newest':
            qset = qset.order_by('-upload_date', '-views')
        elif self.order == 'most_views':
            qset = qset.order_by('-views', '-upload_date')
        else:
            most = Project.objects.order_by('-views')[:1].get().views
            newest = Project.objects.order_by('-id')[:1].get().id
            qset = qset.extra(select={'default_order': "(project_project.id/%s)*(views/%s)"}, select_params=(newest, most)).order_by('-default_order')
            # TODO: Rework default sorting algorithm
            # Problems: Uses IDs, not date. Also should be based of publish_date, not upload_date. Should be normalized values,
            # so the 50% oldest and most viewed post = 70% oldest and 30% most viewed
            # Question: What is the basis? Old relative to: -oldest(date), -unix_stimestamp, -oldest(counter, just how many projects come between)
            # , -newest(to NOW()), how normalize?
            # Views are normalized so that when all projects have the same views, all get 1.0 score. The higher the difference between most
            # and least viewed, the more diverse are the resulting scores. Should this be this way?
            # Maybe even implement a relevancy search like google (number of occurence of tags etc.) in the far future

        qset = qset.distinct()
        qset = qset[:self.maximum]
        #print(qset.query)
        return qset

    def filter_for_tags(self, tags):
        q = Q()
        for tag in tags:
            q &= (Q(search_string__icontains=tag) | Q(tags__value__iexact=tag) | Q(subject__name__iexact=tag) | Q(degree_program__name__iexact=tag)
                  | Q(subject__abbreviation__iexact=tag) | Q(degree_program__abbreviation__iexact=tag)
                  | ((Q(members__show_clear_name=False) & Q(members__unique_name__iexact=tag)) | (Q(members__show_clear_name=True)
                  & Q(members__auth_user__last_name__iexact=tag))) | Q(supervisors__alias__iexact=tag)
                  | Q(projectmember__projectmemberresponsibility__responsibility__value__iexact=tag))
        return q

