"""courserank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include

from marketing.views import (
                            MarketingPreferenceUpdateView, 
                            MailchimpWebhookView,
                            email_list_signup
                        )


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^subscribe/$', email_list_signup, name='email-list-signup'),
    # url(r'^settings/email/$', MarketingPreferenceUpdateView.as_view(), name='marketing-pref'),
    url(r'^u/(?P<code>[a-z0-9].*)/$', MarketingPreferenceUpdateView.as_view(), name='marketing-pref'),
    url(r'^webhooks/mailchimp/$', MailchimpWebhookView.as_view(), name='webhooks-mailchimp'),
    url(r'^', include('accounts.urls')),
    url(r'^accounts/', include('accounts.password.urls')),
    url(r'^blog/', include(('blog.urls', 'blog'), namespace='posts')),
    url(r'^', include(('courses.urls', 'courses'), namespace='course')),
]
