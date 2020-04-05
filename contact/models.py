from django.db import models

# Create your models here.

class Contact(models.Model):
	name 			= models.CharField(max_length=140) 
	email 			= models.EmailField(verbose_name='email address', max_length=255,)
	subject 		= models.CharField(max_length=140)
	message 		= models.TextField()
	updated     	= models.DateTimeField(auto_now=True)
	timestamp   	= models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.email

