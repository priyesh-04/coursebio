from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.urls import reverse

from .utils import unique_slug_generator

from django.utils.safestring import mark_safe
from markdown_deux import markdown
# Create your models here.


class CategoryManager(models.Manager):
    def sorted_categories(self):
    	qs = Category.objects.all()
    	categories = []
    	categories.append(qs.get(title='Computer Science'))
    	categories.append(qs.get(title='Business'))
    	categories.append(qs.get(title='Data Science'))
    	categories.append(qs.get(title='IT & Software'))
    	categories.append(qs.get(title='Marketing'))
    	categories.append(qs.get(title='Office Productivity'))
    	categories.append(qs.get(title='Personal Development'))
    	categories.append(qs.get(title='Finance & Accounting'))
    	categories.append(qs.get(title='Music'))
    	categories.append(qs.get(title='Arts & Design'))
    	categories.append(qs.get(title='Photography'))
    	categories.append(qs.get(title='Health & Fitness'))
    	categories.append(qs.get(title='Lifestyle'))
    	categories.append(qs.get(title='Teaching & Academics'))
    	return categories

class Category(models.Model):
	title				= models.CharField(max_length=100, unique=True)
	image_url 			= models.URLField(null=True, blank=True)
	icon_name			= models.CharField(max_length=100, null=True, blank=True)
	slug       			= models.SlugField(max_length = 255, null=True, unique=True, blank=True)
	updated     		= models.DateTimeField(auto_now=True)
	timestamp   		= models.DateTimeField(auto_now_add=True)

	objects = CategoryManager()

	def __str__(self):
		return str(self.title)

	def get_absolute_url(self):
		return reverse("course:subcategory-list", kwargs={"slug":self.slug})

	def get_home_api_absolute_url(self):
		return reverse("course:home-api", kwargs={"slug":self.slug})


def category_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(category_pre_save_receiver, sender=Category)


class SubCategory(models.Model):
	category			= models.ForeignKey(Category, on_delete=models.CASCADE,)
	title				= models.CharField(max_length=255, unique=True)
	image_url 			= models.URLField(null=True, blank=True)
	slug       			= models.SlugField(max_length = 255, null=True, unique=True, blank=True)
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
	price				= models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True,)
	provider_url		= models.URLField(null=True, blank=True,)
	slug       			= models.SlugField(max_length = 255, null=True, unique=True, blank=True,)
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
	subcategory 	= models.ManyToManyField(SubCategory, blank=True,)
	provider 		= models.ForeignKey(Provider, on_delete=models.CASCADE,)
	image_url       = models.URLField(max_length=500, null=True, blank=True,)
	video_url 		= models.URLField(max_length=500, null=True, blank=True,)
	title			= models.CharField(max_length=255)
	description		= models.TextField()
	author          = models.CharField(max_length=255, null=True, blank=True,)
	duration        = models.CharField(max_length=255, null=True, blank=True,)
	trial			= models.CharField(max_length=255, null=True, blank=True,)
	price			= models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True,)
	level			= models.CharField(max_length=100, null=True, blank=True,)
	rating			= models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True,)
	is_free			= models.BooleanField(default=False,)
	certificate		= models.BooleanField(default=False,)
	course_url		= models.URLField(null=True, blank=True,)
	slug    		= models.SlugField(max_length = 255, null=True, unique=True, blank=True,)
	popular			= models.BooleanField(default=False,)
	updated     	= models.DateTimeField(auto_now=True,)
	timestamp   	= models.DateTimeField(auto_now_add=True,)


	def __str__(self):
		return str(self.title)

	def get_absolute_url(self):
		return reverse("courses:course-detail", 
						kwargs={"slug":self.provider.slug, "slug2":self.slug}
						)
	class Meta:
		ordering = ["-timestamp", "-updated"]

	def get_markdown(self):
		description = self.description
		markdown_text = markdown(description)
		# return mark_safe(markdown_text)
		return description


def course_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(course_pre_save_receiver, sender=Course)