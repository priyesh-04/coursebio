from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task

from .udemy import Udemy

from accounts.models import MyUser
from courses.models import Category, SubCategory, Provider, Course, Topic
from django.conf import settings
from django.core.mail import send_mail

# @task(name="coursebio.tasks.udemy")
def udemy():
	user = MyUser.objects.get(email='priyesh.shukla070@gmail.com')
	provider = Provider.objects.get(title='Udemy')
	present_courses_count = Course.objects.filter(provider__title='Udemy').count()

	udemy = Udemy('A3NMCg6nzLUPjTYR2bIjYeU9cUW1k3wHRQyzTX03', '9PPNGtZy0SPqcLn2mfIltOFzOkqzPQRInEmlLQAtscDkEjadVCO0wwc1Cu2qxMwt4ZlhlMcUZibyIrRx45pWeJmb7KJK4bCt6HgGAolEXDZA94VRpUmkYxWTFMbhB69f')

	udemy_cats = ['Development', 'Design', 'Business', 'Finance+%26+Accounting', 'Health+%26+Fitness', 'IT+%26+Software', 'Lifestyle', 'Marketing', 'Music', 'Office Productivity', 'Personal Development', 'Photography', 'Teaching+%26+Academics',]

	my_cat_dict = {'Development':'Computer Science', 'Design':'Arts & Design', 'Business':'Business', 'Finance+%26+Accounting':'Finance & Accounting', 'Health+%26+Fitness':'Health & Fitness', 'IT+%26+Software':'IT & Software', 'Lifestyle':'Lifestyle', 'Marketing':'Marketing', 'Music':'Music', 'Office Productivity':'Office Productivity', 'Personal Development':'Personal Development', 'Photography':'Photography', 'Teaching+%26+Academics':'Teaching & Academics',}

	for k in range(1,101):
		udemy_course_list = udemy.courses(page=k, page_size=100,category='Teaching+%26+Academics')
		# print(udemy_cats[cats],'list')
		try:
			for i in range(len(udemy_course_list['results'])):
				
				udemy_course_detail = udemy.course_detail(udemy_course_list['results'][i]['id'], course ='@all')
				course_ = ''
				try:
					course_ = Course.objects.get(title=udemy_course_detail['title'])
				except Exception as e:
					print(e,'Exception line 35')
				# print('Detail',udemy_course_detail,'Detail')
				if course_:
					course_obj = course_
					category = Category.objects.get(title='Teaching & Academics')
					course_obj.category = category
					try:
						num_subscribers = udemy_course_detail['num_subscribers']
						course_obj.num_subscribers = num_subscribers
						if num_subscribers > 5000:
							course_obj.is_popular = True
					except Exception as e:
						print(e,'Exception line 84')

					try:
						rating = udemy_course_detail['avg_rating']
						num_reviews = udemy_course_detail['num_reviews']
						course_obj.rating = rating
						course_obj.num_reviews = num_reviews
					except Exception as e:
						print(e,'Exception line 92')
						
					course_obj.save()
					subcategory = ''
					try:
						subcategory = SubCategory.objects.get(title=udemy_course_detail['primary_subcategory']['title'])
					except Exception as e:
						print(e,'Exception line 45')
					if not subcategory:
						subcat_obj = SubCategory.objects.create(category=category,title=udemy_course_detail['primary_subcategory']['title'])
						course_obj.subcategory.add(subcat_obj)
						print(subcat_obj,'subcategory added')
					else:
						course_obj.subcategory.add(subcategory)
						print(subcategory,'subcategory added')

					d = udemy_course_detail['course_has_labels']
					topic = ''
					for j in range(len(d)):
						try:
							topic = Topic.objects.get(title=d[j]['label']['title'])
						except Exception as e:
							print(e,'Exception line 58')
						if not topic:
							topic_obj = Topic.objects.create(category=category,title=d[j]['label']['title'])
							course_obj.topic.add(topic_obj)
							print(topic_obj,'topic added')
						else:
							course_obj.topic.add(topic)
							print(topic,'topic added')

				
				elif not course_:
					# print('Total',i,'courses added in database.')
					try:
						category = Category.objects.get(title='Teaching & Academics')
						image = udemy_course_detail['image_480x270']
						author = udemy_course_detail['visible_instructors'][0]['title']
						duration = udemy_course_detail['content_info']
						level = udemy_course_detail['instructional_level']
						url = 'https://www.udemy.com' + udemy_course_detail['url']
						course_obj = Course(user=user, category=category, provider=provider, image_url=image, title=udemy_course_detail['title'], description=udemy_course_detail['description'], author=author, duration=duration, level=level, course_url=url)
						try:
							num_subscribers = udemy_course_detail['num_subscribers']
							course_obj.num_subscribers = num_subscribers
							if num_subscribers > 5000:
								course_obj.is_popular = True
						except Exception as e:
							print(e,'Exception line 84')

						try:
							rating = udemy_course_detail['avg_rating']
							num_reviews = udemy_course_detail['num_reviews']
							course_obj.rating = rating
							course_obj.num_reviews = num_reviews
						except Exception as e:
							print(e,'Exception line 92')

						try:
							video = udemy_course_detail['promo_asset']['download_urls']['Video'][0]['file']
							course_obj.video_url = video
						except Exception as e:
							print(e,'Exception video not available line 90')

						if udemy_course_detail['is_paid']:
							course_obj.price = 13.0
						else:
							course_obj.is_free=True
						course_obj.has_certificate = True
						course_obj.save()
						subcategory = ''
						try:
							subcategory = SubCategory.objects.get(title=udemy_course_detail['primary_subcategory']['title'])
						except Exception as e:
							print(e,'Exception line 67')
						if not subcategory:
							subcat_obj = SubCategory.objects.create(category=category,title=udemy_course_detail['primary_subcategory']['title'])
							course_obj.subcategory.add(subcat_obj)
						else:
							course_obj.subcategory.add(subcategory)

						d = udemy_course_detail['course_has_labels']
						topic = ''
						for j in range(len(d)):
							try:
								topic = Topic.objects.get(title=d[j]['label']['title'])
							except Exception as e:
								print(e,'Exception line 80')
							if not topic:
								topic_obj = Topic.objects.create(category=category,title=d[j]['label']['title'])
								course_obj.topic.add(topic_obj)
							else:
								course_obj.topic.add(topic)
						course_obj.save()
					except Exception as e:
						print(e,'Exception line 114')
						continue

		except Exception as e:
			print(e,'Exception line 118')
			continue
			

	updated_courses_count = Course.objects.filter(provider__title='udemy').count()
	if present_courses_count == updated_courses_count:
		subject = 'All courses already exists in our database.'
		from_email = settings.EMAIL_HOST_USER
		message = 'Not found any new course to add in our database.All courses already exists in our database'
		recipient_list = ['tecnicotrixx@gmail.com', 'priyesh.shukla070@hotmail.com']
		html_message = '<h1>No new course found to add in our database.</h1>'
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

	subject = 'Successfully completed udemy course adding feature.'
	from_email = settings.EMAIL_HOST_USER
	message = 'Udemy api process completed.'
	recipient_list = ['tecnicotrixx@gmail.com', 'priyesh.shukla070@hotmail.com']
	html_message = '<h1>Udemy api process completed.</h1>' + message
	return send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)
    