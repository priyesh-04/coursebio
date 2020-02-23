from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.core.validators import RegexValidator
from django.db.models.signals import post_save, pre_save
from accounts.utils import unique_slug_generator


USERNAME_REGEX = '^[a-zA-Z0-9.+-_]*$'


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, firstname, lastname, date_of_birth, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
        	raise ValueError('username is required.')

        user = self.model(
        	username=username,
            email=self.normalize_email(email),
            firstname=firstname,
            lastname=lastname,
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, firstname, lastname, date_of_birth, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
        	username,
            email,
            firstname=firstname,
            lastname=lastname,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
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
    date_of_birth 	= models.DateField()
    slug            = models.SlugField(null=True, unique=True, blank=True)
    is_active 		= models.BooleanField(default=True)
    is_admin 		= models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'firstname', 'lastname', 'date_of_birth']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


def myuser_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(myuser_pre_save_receiver, sender=MyUser)