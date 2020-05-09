from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task

from .udemy import Udemy

from accounts.models import MyUser
from courses.models import Category, SubCategory, Provider, Course
from django.conf import settings
from django.core.mail import send_mail

# @task(name="coursebio.tasks.udemy")
def udemy():
	user = MyUser.objects.get(email='priyesh.shukla070@gmail.com')
	provider = Provider.objects.get(title='udemy')
	present_courses_count = Course.objects.filter(provider__title='udemy').count()

	udemy = Udemy('A3NMCg6nzLUPjTYR2bIjYeU9cUW1k3wHRQyzTX03', '9PPNGtZy0SPqcLn2mfIltOFzOkqzPQRInEmlLQAtscDkEjadVCO0wwc1Cu2qxMwt4ZlhlMcUZibyIrRx45pWeJmb7KJK4bCt6HgGAolEXDZA94VRpUmkYxWTFMbhB69f')

	udemy_cats = ['Development', 'Design', 'Business', 'Finance+%26+Accounting', 'Health+%26+Fitness', 'IT+%26+Software', 'Lifestyle', 'Marketing', 'Music', 'Office Productivity', 'Personal Development', 'Photography', 'Teaching+%26+Academics',]

	my_cat_dict = {'Development':'Computer Science', 'Design':'Arts & Design', 'Business':'Business', 'Finance+%26+Accounting':'Finance & Accounting', 'Health+%26+Fitness':'Health & Fitness', 'IT+%26+Software':'IT & Software', 'Lifestyle':'Lifestyle', 'Marketing':'Marketing', 'Music':'Music', 'Office Productivity':'Office Productivity', 'Personal Development':'Personal Development', 'Photography':'Photography', 'Teaching+%26+Academics':'Teaching & Academics',}

	for cats in range(len(udemy_cats)):
		for k in range(1,101):
			udemy_course_list = udemy.courses(page=k, page_size=100,category=udemy_cats[cats])
			# print(udemy_cats[cats],'list')
			for i in range(len(udemy_course_list['results'])):
				
				udemy_course_detail = udemy.course_detail(udemy_course_list['results'][i]['id'], course ='@all')
				course_ = Course.objects.filter(title=udemy_course_detail['title'])
				# print('Detail',udemy_course_detail,'Detail')
				if course_:
					i=i+1
					continue
				
				elif not course_:
					# print('Total',i,'courses added in database.')
					category = Category.objects.get(title=my_cat_dict[udemy_cats[cats]])
					image = udemy_course_detail['image_480x270']
					author = udemy_course_detail['visible_instructors'][0]['title']
					duration = udemy_course_detail['content_info']
					level = udemy_course_detail['instructional_level']
					url = 'https://www.udemy.com/' + udemy_course_detail['url']
					course_obj = Course(user=user, category=category, provider=provider, image_url=image, title=udemy_course_detail['title'], description=udemy_course_detail['description'], author=author, duration=duration, level=level, course_url=url)
					
					try:
						video = udemy_course_detail['promo_asset']['download_urls']['Video'][0]['file']
						course_obj.video_url = video
					except Exception as e:
						print(e,'Exception')
					if udemy_course_detail['is_paid']:
						course_obj.price = 13.0
					else:
						course_obj.is_free=True
					course_obj.certificate = True
					course_obj.save()
					d = udemy_course_detail['course_has_labels']

					for j in range(len(d)):

						subcategory = SubCategory.objects.filter(title=d[j]['label']['title'])
						if not subcategory:
							new_subcat = SubCategory.objects.create(category=category,title=d[j]['label']['title'])
							course_obj.subcategory.add(new_subcat)
						else:
							course_obj.subcategory.add(subcategory[0])
			

	updated_courses_count = Course.objects.filter(provider__title='udemy').count()
	if present_courses_count == updated_courses_count:
		subject = 'All courses already exists in our database.'
		from_email = settings.EMAIL_HOST_USER
		message = 'Not found any new course to add in our database.All courses already exists in our database'
		recipient_list = ['tecnicotrixx@gmail.com', 'priyesh.shukla070@gmail.com']
		html_message = '<h1>No new course found to add in our database.</h1>'
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

	subject = 'Successfully completed udemy course adding feature.'
	from_email = settings.EMAIL_HOST_USER
	message = 'Udemy api process completed.'
	recipient_list = ['tecnicotrixx@gmail.com', 'priyesh.shukla070@gmail.com']
	html_message = '<h1>Udemy api process completed.</h1>' + message
	return send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)
    