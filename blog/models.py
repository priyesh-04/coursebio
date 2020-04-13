from __future__ import unicode_literals

from django.conf import settings
# from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from courses.utils import unique_slug_generator


from markdown_deux import markdown
# from comments.models import Comment

from .utils import get_read_time


class BlogCategory(models.Model):
    title               = models.CharField(max_length=100, unique=True)
    slug                = models.SlugField(max_length = 255, null=True, unique=True, blank=True)
    updated             = models.DateTimeField(auto_now=True)
    timestamp           = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse("posts:category-posts", kwargs={"slug":self.slug})


def category_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(category_pre_save_receiver, sender=BlogCategory)

class PostManager(models.Manager):
    def active(self, *args, **kwargs):
        # Post.objects.all() = super(PostManager, self).all()
        return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now())


class Post(models.Model):
    user 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    category        = models.ForeignKey(BlogCategory, null=True, blank=True, on_delete=models.CASCADE,)
    title 			= models.CharField(max_length=120, unique=True)
    image_url 		= models.URLField(null=True, blank=True)
    content 		= models.TextField()
    draft 			= models.BooleanField(default=False)
    slug 			= models.SlugField(max_length = 255, null=True, unique=True, blank=True)
    publish 		= models.DateField(auto_now=False, auto_now_add=False)
    read_time 		= models.IntegerField(default=0) # models.TimeField(null=True, 														blank=True) #assume minutes
    updated 		= models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp 		= models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = PostManager()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:detail", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["-timestamp", "-updated"]

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

    # @property
    # def comments(self):
    #     instance = self
    #     qs = Comment.objects.filter_by_instance(instance)
    #     return qs

    # @property
    # def get_content_type(self):
    #     instance = self
    #     content_type = ContentType.objects.get_for_model(instance.__class__)
    #     return content_type


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if instance.content and not instance.slug:
        html_string = instance.get_markdown()
        read_time_var = get_read_time(html_string)
        instance.read_time = read_time_var

        instance.slug = unique_slug_generator(instance)


pre_save.connect(pre_save_post_receiver, sender=Post)










