from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.views.generic import (
									CreateView, 
									FormView, 
									DetailView, 
									View, 
									UpdateView
								)
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
# from accounts.mixins import NextUrlMixin, RequestFormAttachMixin
from accounts.forms import UserLoginForm, UserCreationForm

# Create your views here.


# class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
#     form_class = LoginForm
#     success_url = '/'
#     template_name = 'accounts/login.html'
#     default_next = '/'

#     def form_valid(self, form):
#         next_path = self.get_next_url()
#         return redirect(next_path)

# class LoginView(LoginRequiredMixin, View):
#     login_url = '/login/'
    # redirect_field_name = '/'


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'accounts/register.html'
    success_url = '/accounts/login/'



# def register(request, *args, **kwargs):
#     form = UserCreationForm(request.POST or None)
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/login")
#     return render(request, "accounts/register.html", {"form": form})


def login_view(request, *args, **kwargs):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        user_obj = form.cleaned_data.get('user_obj')
        login(request, user_obj)
        print('loggedin successfully')
        return HttpResponseRedirect("/")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/accounts/login/")