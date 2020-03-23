from django.conf.urls import url
from django.contrib import admin


from accounts.views import (login_view,
							RegisterView,
							logout_view,
							UserDetailView,
							UserUpdateView
							)

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='register'),
    # url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^user/(?P<username>[\w.@+-]+)/$', UserDetailView.as_view(), name='detail'),
    url(r'^update/(?P<username>[\w.@+-]+)/$', UserUpdateView.as_view(), name='update'),
]