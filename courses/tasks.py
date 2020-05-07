from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task

from .udemy import Udemy

from accounts.models import MyUser
from courses.models import Category, SubCategory, Provider, Course

# @task(name="sum_two_numbers")
# def add(x, y):
#     return x + y

# @task(name="multiply_two_numbers")
# def mul(x, y):
#     total = x * (y * random.randint(3, 100))
#     return total

# @task(name="sum_list_numbers")
# def xsum(numbers):
#     return sum(numbers)

@task(name="udemy_api")
def udemyapi():
	user = MyUser.objects.filter(id=1)[0]
	category = Category.objects.filter(id=3)[0]
	provider=Provider.objects.filter(id=1)[0]

	udemy = Udemy('A3NMCg6nzLUPjTYR2bIjYeU9cUW1k3wHRQyzTX03', '9PPNGtZy0SPqcLn2mfIltOFzOkqzPQRInEmlLQAtscDkEjadVCO0wwc1Cu2qxMwt4ZlhlMcUZibyIrRx45pWeJmb7KJK4bCt6HgGAolEXDZA94VRpUmkYxWTFMbhB69f')

	udemy_course_list = udemy.courses(page=1, page_size=25,category='Lifestyle')
	for i in range(len(udemy_course_list['results'])):
		
		udemy_course_detail = udemy.course_detail(udemy_course_list['results'][i]['id'], course ='@all')
		course_ = Course.objects.filter(title=udemy_course_detail['title'])

		if course_:
			i=i+1
			continue
		
		elif not course_:
			print('Total',i,'courses added in database.')
			course_obj = Course(user=user, category=category, provider=provider,title=udemy_course_detail['title'],description=udemy_course_detail['description'],)
			course_obj.save()
			d = udemy_course_detail['course_has_labels']

			for i in range(len(d)):

				subcategory = SubCategory.objects.filter(title=d[i]['label']['title'])
				if not subcategory:
					new_subcat = SubCategory.objects.create(category=category,title=d[i]['label']['title'])
					course_obj.subcategory.add(new_subcat)
				else:
					course_obj.subcategory.add(subcategory[0])

		else:
			print('All courses already exists in our database.')
	return None
    