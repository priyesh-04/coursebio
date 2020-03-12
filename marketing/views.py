from django.conf import settings

from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.views.generic import UpdateView, View, CreateView
from django.shortcuts import render, redirect


from .forms import MarketingPreferenceForm, EmailSignupForm
from .mixins import CsrfExemptMixin
from .models import MarketingPreference
from .utils import Mailchimp
MAILCHIMP_EMAIL_LIST_ID = getattr(settings, "MAILCHIMP_EMAIL_LIST_ID", None)

class MarketingPreferenceUpdateView(SuccessMessageMixin, UpdateView):
    form_class = MarketingPreferenceForm
    template_name = 'base/subscribe/unsubscribe.html' # yeah create this
    success_url = '/login/'
    success_message = 'Your email preferences have been updated. Thank you.'

    def dispatch(self, *args, **kwargs):
        # user = self.request.user
        url_key = self.request.resolver_match.kwargs['code']
        user_key = MarketingPreference.objects.filter(key=url_key)
        # print(user_key)
        if not user_key:
            return redirect("/login/") # HttpResponse("Not allowed", status=400)
        return super(MarketingPreferenceUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(MarketingPreferenceUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Update Email Preferences'
        return context

    def get_object(self):
        url_key = self.request.resolver_match.kwargs['code']
        # user_key = MarketingPreference.objects.filter(key=url_key)
        obj, created = MarketingPreference.objects.get_or_create(key=url_key)
        # print(obj, created,'hello')
        # get_absolute_url
        return obj

def email_list_signup(request):
    form = EmailSignupForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            email_signup_qs = MarketingPreference.objects.filter(email=request.POST['email'])
            email_signup = email_signup_qs.first()
            if email_signup_qs.exists():
                if email_signup.subscribed:
                    messages.info(request, "You are already subscribed")
                else:
                    status_code, response_data = Mailchimp().subscribe(request.POST['email'])
                    # print(status_code, response_data,'update sub res')
                    if status_code == 200:
                        email_signup.subscribed = True
                        email_signup.mailchimp_subscribed = True
                        email_signup.mailchimp_msg = response_data
                        email_signup.save()
            else:
                obj = MarketingPreference()
                status_code, response_data = Mailchimp().subscribe(request.POST['email'])
                # print(status_code, response_data,'create sub res')
                if status_code == 200:
                    obj.email = request.POST['email']
                    obj.subscribed = True
                    obj.mailchimp_subscribed = True
                    obj.mailchimp_msg = response_data
                    obj.save()
                else:
                    messages.info(request, f"{response_data['detail']}")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



"""
POST METHOD
data[list_id]: e2ef12efee
fired_at: 2017-10-18 18:49:49
data[merges][FNAME]:
data[email]: hello@teamcfe.com
data[merges][LNAME]:
data[email_type]: html
data[reason]: manual
data[merges][BIRTHDAY]:
data[id]: d686033a32
data[merges][EMAIL]: hello@teamcfe.com
data[ip_opt]: 108.184.68.3
data[web_id]: 349661
type: unsubscribe
data[action]: unsub
"""

class MailchimpWebhookView(CsrfExemptMixin, View): # HTTP GET -- def get() CSRF?????
    # def get(self, request, *args, **kwargs):
    #     return HttpResponse("Thank you", status=200)
    def post(self, request, *args, **kwargs):
        data = request.POST
        list_id = data.get('data[list_id]')
        if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
            hook_type = data.get("type")
            email = data.get('data[email]')
            response_status, response = Mailchimp().check_subcription_status(email)
            sub_status  = response['status']
            is_subbed = None
            mailchimp_subbed = None
            if sub_status == "subscribed":
                is_subbed, mailchimp_subbed  = (True, True)
            elif sub_status == "unsubscribed":
                is_subbed, mailchimp_subbed  = (False, False)
            if is_subbed is not None and mailchimp_subbed is not None:
                qs = MarketingPreference.objects.filter(user__email__iexact=email)
                if qs.exists():
                    qs.update(
                            subscribed=is_subbed, 
                            mailchimp_subscribed=mailchimp_subbed, 
                            mailchimp_msg=str(data))
        return HttpResponse("Thank you", status=200)

# def mailchimp_webhook_view(request):
#     data = request.POST
#     list_id = data.get('data[list_id]')
#     if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
#         hook_type = data.get("type")
#         email = data.get('data[email]')
#         response_status, response = Mailchimp().check_subcription_status(email)
#         sub_status  = response['status']
#         is_subbed = None
#         mailchimp_subbed = None
#         if sub_status == "subscribed":
#             is_subbed, mailchimp_subbed  = (True, True)
#         elif sub_status == "unsubscribed":
#             is_subbed, mailchimp_subbed  = (False, False)
#         if is_subbed is not None and mailchimp_subbed is not None:
#             qs = MarketingPreference.objects.filter(user__email__iexact=email)
#             if qs.exists():
#                 qs.update(
#                         subscribed=is_subbed, 
#                         mailchimp_subscribed=mailchimp_subbed, 
#                         mailchimp_msg=str(data))
#     return HttpResponse("Thank you", status=200)



