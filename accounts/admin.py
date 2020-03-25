from django.contrib import admin
from django import forms

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import MyUser



class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm
     # fields = (
     #        'id',
     #        'firstname',
     #        'lastname',
     #        'username',
     #        'email',
     #        'date_of_birth',
     #        'is_admin',
     #        'slug',
     #    )

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'username', 'email', 'firstname', 'lastname', 'date_of_birth', 'is_admin')
    list_filter = ('is_admin','is_active')
    list_display_links = ('id', 'username')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Personal info'), {'fields': ('firstname', 'lastname')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('username', 'email',)
    ordering = ('username',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(MyUser, UserAdmin)

# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)

# fieldsets = (
#         (None, {'fields': (
#                         'firstname',
#                         'lastname',
#                         'username',
#                         'email',
#                         'password',
#                         'slug',
#                     )}),
#         ('Personal info', {'fields': ('date_of_birth',)}),
#         ('Permissions', {'fields': ('is_admin',)}),
#         ('Access', {'fields': ('is_active',)}),
#     )
#     # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
#     # overrides get_fieldsets to use this attribute when creating a user.
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'date_of_birth', 'password1', 'password2')}
#         ),
#     )