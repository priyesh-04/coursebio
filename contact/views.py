from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin

from .forms import ContactUsCreationForm
# Create your views here.


class ContactUs(SuccessMessageMixin, CreateView):
    form_class = ContactUsCreationForm
    template_name = 'contact/contact-us.html'
    success_url = '/'
    success_message = "Thank you %(name)s. We have recieved your request. We will get back to you very soon."