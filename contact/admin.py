from django.contrib import admin

# Register your models here.
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'email', 'subject','updated',)
	list_display_links = ('email', 'id', 'name',)
	list_filter = ('timestamp', 'updated', 'email',)
	search_fields = ('email', 'subject',)
	ordering = ('-timestamp',)

admin.site.register(Contact, ContactAdmin)