from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.urls import reverse

from .utils import unique_slug_generator
# Create your models here.

class Category(models.Model):
	title				= models.CharField(max_length=100, unique=True)
	image_url 			= models.URLField(null=True, blank=True)
	icon_name			= models.CharField(max_length=100, null=True, blank=True)
	slug       			= models.SlugField(null=True, unique=True, blank=True)
	updated     		= models.DateTimeField(auto_now=True)
	timestamp   		= models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return str(self.title)

	def get_absolute_url(self):
		return reverse("course:subcategory-list", kwargs={"slug":self.slug})


def category_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(category_pre_save_receiver, sender=Category)


class SubCategory(models.Model):
	category			= models.ForeignKey(Category, on_delete=models.CASCADE,)
	title				= models.CharField(max_length=100, unique=True)
	description			= models.TextField(null=True, blank=True)
	image_url 			= models.URLField(null=True, blank=True)
	slug       			= models.SlugField(null=True, unique=True, blank=True)
	updated     		= models.DateTimeField(auto_now=True)
	timestamp   		= models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return str(self.title)

	def get_absolute_url(self):
		return reverse("course:course-list", kwargs={"slug":self.category.slug,"slug2":self.slug})


def subcategory_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(subcategory_pre_save_receiver, sender=SubCategory)


class Provider(models.Model):
	title				= models.CharField(max_length=100,)
	image_url 			= models.URLField(null=True, blank=True,)
	plan_details        = models.CharField(max_length=140, null=True, blank=True,)
	slug       			= models.SlugField(null=True, unique=True, blank=True,)
	updated     		= models.DateTimeField(auto_now=True,)
	timestamp   		= models.DateTimeField(auto_now_add=True,)


	def __str__(self):
		return str(self.title)

	# def get_absolute_url(self):
	# 	return reverse("courses:course-list", 
	# 					kwargs={"slug":self.category.slug}
	# 					)

def provider_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(provider_pre_save_receiver, sender=Provider)



class Course(models.Model):
	user			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
	category 		= models.ForeignKey(Category, on_delete=models.CASCADE,)
	subcategory 	= models.ForeignKey(SubCategory, on_delete=models.CASCADE,)
	provider 		= models.ForeignKey(Provider, on_delete=models.CASCADE,)
	image_url       = models.URLField(null=True, blank=True,)
	video_url 		= models.URLField(null=True, blank=True,)
	title			= models.CharField(max_length=200, unique=True,)
	description		= models.TextField()
	author          = models.CharField(max_length=120, null=True, blank=True,)
	duration        = models.CharField(max_length=50, null=True, blank=True,)
	trial			= models.CharField(max_length=50, null=True, blank=True,)
	price			= models.DecimalField(max_digits=19, decimal_places=2,)
	slug    		= models.SlugField(null=True, unique=True, blank=True,)
	updated     	= models.DateTimeField(auto_now=True,)
	timestamp   	= models.DateTimeField(auto_now_add=True,)

	def __str__(self):
		return str(self.title)

	def get_absolute_url(self):
		return reverse("courses:course-detail", 
						kwargs={"slug":self.provider.slug, "slug2":self.slug}
						)


def course_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(course_pre_save_receiver, sender=Course)