#AYOUB AR
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from .utils import MailChimp

User = settings.AUTH_USER_MODEL


class Marketing(models.Model):
	user          			= models.OneToOneField(User, on_delete=models.DO_NOTHING)
	subscribed    			= models.BooleanField(default=True)
	mailchimp_subscribed    = models.NullBooleanField(blank=True)
	mailchimp_msg 			= models.TextField(null=True, blank=True)
	timestamp     			= models.DateTimeField(auto_now_add=True)
	updated       			= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.user.email


def marketing_pref_create_receiver(sender, instance, created, *args, **kwargs):
	if created:
		status_code, response_data = MailChimp().subscribe(instance.user.email)
		print(status_code, response_data)
post_save.connect(marketing_pref_create_receiver, sender=Marketing)


def marketing_pref_update_receiver(sender, instance, *args, **kwargs):
	if instance.subscribed != instance.mailchimp_subscribed:
		if instance.subscribed:
			status_code, response_data = MailChimp().subscribe(instance.user.email)
		else:
			status_code, response_data = MailChimp().unsubscribe(instance.user.email)

		if response_data['status'] == "subscribed":
			# subscribing user
			instance.subscribed = True
			instance.mailchimp_subscribed = True
			instance.mailchimp_msg = response_data
		else:
			# unsubscribing user
			instance.subscribed = False
			instance.mailchimp_subscribed = False
			instance.mailchimp_msg = response_data

pre_save.connect(marketing_pref_update_receiver, sender=Marketing)
