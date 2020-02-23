from django.shortcuts import render
from django.views.generic import (
									CreateView, 
									FormView, 
									DetailView, 
									View, 
									UpdateView
								)

from accounts.mixins import NextUrlMixin, RequestFormAttachMixin
from accounts.forms import LoginForm, RegisterForm, UserDetailChangeForm

# Create your views here.


class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = 'accounts/login.html'
    default_next = '/'

    def form_valid(self, form):
        next_path = self.get_next_url()
        return redirect(next_path)




class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'