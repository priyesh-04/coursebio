from django.contrib import admin

# Register your models here.
from blog.models import BlogCategory, Post

from django.db import models

from blog.forms import AdminPostForm

from pagedown.widgets import AdminPagedownWidget

admin.site.register(BlogCategory)

@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget},
    }

