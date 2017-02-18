from django.db import models
from MTShowcase.settings import STATIC_URL


def user_directory_path(instance, filename):
    # MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/avatar/{1}'.format(
        instance.id,
        filename
    )


class User(models.Model):
    # CHOICES
    STUDENT = 'student'
    PROF = 'professor'
    ADMIN = 'admin'

    USER_TYPE = (
        (STUDENT, 'Student'),
        (PROF, 'Professor'),
        (ADMIN, 'Admin')
    )
    # related field to the "auth user"
    auth_user = models.OneToOneField('authentication.AuthEmailUser', on_delete=models.CASCADE)

    # DISPLAYED CONTENT
    alias = models.CharField(max_length=50, blank=True, null=True)  # TODO: Remove
    unique_name = models.CharField(max_length=60, unique=True)  # For URL to access user profile
    socials = models.ManyToManyField('Social', through='UserSocial', through_fields=('user', 'social'),
                                     related_name='user_social')

    profile_img = models.ImageField(upload_to=user_directory_path, null=True, blank=True, default=STATIC_URL + 'images/demoavatar.png')

    # flags to control user privacy
    show_clear_name = models.BooleanField(default=True)

    # META DATA
    type = models.CharField(choices=USER_TYPE, default=STUDENT, max_length=25)

    def __str__(self):
        return "ID: {} (Auth User: {} ({})) - {} ({}) - Type: {}".format(
            self.id,
            self.auth_user.id,
            self.auth_user.email,
            self.unique_name,
            "Name sichtbar" if self.show_clear_name else "Name versteckt",
            self.type
        )

    def get_public_name(self):
        if self.show_clear_name:
            return "{0} {1}".format(
                self.auth_user.first_name,
                self.auth_user.last_name
            )

        else:
            return self.unique_name

    def is_admin_or_prof(self):
        return self.type == User.ADMIN or self.type == User.PROF

    def save(self, *args, **kwargs):
        # delete old image on update if exists
        try:
            this = User.objects.get(id=self.id)
            if this.profile_img != self.profile_img:
                this.profile_img.delete(save=False)

        except:
            pass
        super(User, self).save(*args, **kwargs)


class Social(models.Model):
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=50)
    icon = models.TextField(max_length=255, default='circle-o')

    def __str__(self):
        return "ID: {} - {}".format(
            self.id,
            self.name.capitalize()
        )

    def get_icon_path(self):
        return "{0}{1}{2}".format(
            STATIC_URL,
            "project/images/icons/",
            self.icon
        )


class UserSocial(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    social = models.ForeignKey('Social', on_delete=models.CASCADE)
    url = models.URLField()

    def __str__(self):
        return "{} (ID: {}) - {} (ID: {}): {}".format(
            self.user.unique_name,
            self.user.id,
            self.social.display_name,
            self.social.id, self.url
        )

