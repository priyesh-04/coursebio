from django.contrib import admin

# Register your models here
from .models import (
						Category, 
						SubCategory, 
						Course, 
						Provider,
					)

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'slug', 'updated',)
	list_display_links = ('title', 'id')
	list_filter = ('timestamp', 'updated')
	search_fields = ('title',)
	ordering = ('-timestamp',)

class SubCategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'category', 'slug', 'updated',)
	list_display_links = ('title', 'id')
	list_filter = ('timestamp', 'updated')
	search_fields = ('title',)
	ordering = ('-timestamp',)


class ProviderAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'slug', 'updated',)
	list_display_links = ('title', 'id')
	list_filter = ('timestamp', 'updated')
	search_fields = ('title',)
	ordering = ('-timestamp',)


class CourseAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'price', 'provider', 'subcategory', 'category', 'slug', 'updated',)
	list_display_links = ('title', 'category', 'id')
	list_filter = ('category', 'price', 'provider', 'subcategory', 'timestamp', 'updated')
	search_fields = ('category__title', 'subcategory__title', 'title', 'description')
	ordering = ('-timestamp',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Course, CourseAdmin)