from django.contrib import admin

# Register your models here
from django.db import models

from pagedown.widgets import AdminPagedownWidget

from .models import (
						Category, 
						SubCategory, 
						Course, 
						Provider,
						Topic,
					)

# @admin.register(Course)
# class PostModelAdmin(admin.ModelAdmin):
#     formfield_overrides = {
#         models.TextField: {'widget': AdminPagedownWidget},
#     }

class CourseAdmin(admin.ModelAdmin):
	formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget},
    }
	list_display = ('id', 'title', 'provider', 'category', 'user', 'timestamp', 'updated',)
	list_display_links = ('title', 'category', 'id')
	list_filter = ('user', 'category', 'subcategory', 'provider', 'timestamp', 'updated')
	search_fields = ('category__title', 'subcategory__title', 'title', 'description')
	ordering = ('-timestamp',)

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'slug', 'timestamp', 'updated',)
	list_display_links = ('title', 'id')
	list_filter = ('timestamp', 'updated')
	search_fields = ('title',)
	ordering = ('-timestamp',)

class SubCategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'category', 'slug', 'updated',)
	list_display_links = ('title', 'id')
	list_filter = ('category__title', 'timestamp', 'updated')
	search_fields = ('category__title', 'title',)
	ordering = ('-timestamp',)

class TopicAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'category', 'slug', 'updated',)
	list_display_links = ('title', 'id')
	list_filter = ('category__title', 'subcategory__title', 'timestamp', 'updated')
	search_fields = ('category__title', 'subcategory__title', 'title',)
	ordering = ('-timestamp',)


class ProviderAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'slug', 'updated',)
	list_display_links = ('title', 'id')
	list_filter = ('timestamp', 'updated')
	search_fields = ('title',)
	ordering = ('-timestamp',)





admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Course, CourseAdmin)