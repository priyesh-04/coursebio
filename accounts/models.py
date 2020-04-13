from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils import timezone
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db.models.signals import post_save, pre_save
from accounts.utils import unique_slug_generator


USERNAME_REGEX = '^[a-zA-Z0-9.+-_]*$'


class MyUserManager(BaseUserManager):
    def _create_user(self, email, password,
                     is_staff, is_admin, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, 
                          is_active=True, 
                          is_admin=is_admin,
                          is_superuser=is_superuser, 
                          last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, False
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, True,
                                 **extra_fields)


class MyUser(AbstractBaseUser, PermissionsMixin):
    email           = models.EmailField(
                                        verbose_name='email address',
                                        max_length=255,
                                        unique=True,
                                    )
    username        = models.CharField(max_length=255, 
                                            validators=[
                                            RegexValidator(
                                                regex = USERNAME_REGEX,
                                                message = 'Username must be Alpahnumeric or contain any of the following: ". @ + -" ',
                                                code='invalid_username'
                                            )],
                                        unique=True,
                                        )
    firstname       = models.CharField(max_length=255, blank=True)
    lastname        = models.CharField(max_length=255, blank=True)
    date_of_birth 	= models.DateField(blank=True, null=True)
    slug            = models.SlugField(max_length = 255, null=True, unique=True, blank=True)
    is_staff        = models.BooleanField(('staff status'), default=False,
                    help_text=('Designates whether the user can log into this admin '
                    'site.'))
    is_active       = models.BooleanField(('active'), default=True,
                    help_text=('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    is_admin 		= models.BooleanField(default=False)
    date_joined     = models.DateTimeField(('date joined'), default=timezone.now)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'firstname', 'lastname', 'date_of_birth']

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.firstname, self.lastname)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.firstname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_admin


def myuser_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(myuser_pre_save_receiver, sender=MyUser)