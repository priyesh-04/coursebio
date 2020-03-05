from django.db import models
from django.db.models.signals import post_save, pre_save

from .utils import Mailchimp
from accounts.models import MyUser

class MarketingPreference(models.Model):
    user                        = models.OneToOneField(MyUser, on_delete=models.CASCADE, null=True, blank=True,)
    email                       = models.EmailField()
    subscribed                  = models.BooleanField(default=True)
    mailchimp_subscribed        = models.NullBooleanField(blank=True)
    mailchimp_msg               = models.TextField(null=True, blank=True)
    key                         = models.CharField(max_length=120)
    timestamp                   = models.DateTimeField(auto_now_add=True)
    updated                     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email



from accounts.utils import code_generator
def marketing_pref_create_receiver(sender, instance, created, *args, **kwargs):
    if not instance.key:
        instance.key = code_generator()
    if not instance.email:
        instance.email = instance.user.email
    if created:
        if instance.user:
            status_code, response_data = Mailchimp().subscribe(instance.user.email)
        else:
            status_code, response_data = Mailchimp().subscribe(instance.email)
        # print(status_code, response_data,'sc res')


post_save.connect(marketing_pref_create_receiver, sender=MarketingPreference)

def marketing_pref_update_receiver(sender, instance, *args, **kwargs):
    if not instance.key:
        instance.key = code_generator()
    if not instance.email:
        instance.email = instance.user.email
    if instance.subscribed != instance.mailchimp_subscribed:
        if instance.subscribed:
            # subscribing user
            if instance.user:
                status_code, response_data = Mailchimp().subscribe(instance.user.email)
            else:
                status_code, response_data = Mailchimp().subscribe(instance.email)
        else:
            # unsubscribing user
            if instance.user:
                status_code, response_data = Mailchimp().unsubscribe(instance.user.email)
            else:
                status_code, response_data = Mailchimp().unsubscribe(instance.email)
        # print(status_code, response_data,'sc res')
        if response_data['status'] == 'subscribed':
            instance.subscribed = True
            instance.mailchimp_subscribed = True
            instance.mailchimp_msg = response_data
        else:
            instance.subscribed = False
            instance.mailchimp_subscribed = False
            instance.mailchimp_msg = response_data

pre_save.connect(marketing_pref_update_receiver, sender=MarketingPreference)



def make_marketing_pref_receiver(sender, instance, created, *args, **kwargs):
    '''
    User model
    '''
    if created:
        obj, created = MarketingPreference.objects.get_or_create(user=instance)
        
post_save.connect(make_marketing_pref_receiver, sender=MyUser)

