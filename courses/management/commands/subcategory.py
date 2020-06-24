# command to reassociate courses to right category and subcategory

from django.core.management.base import BaseCommand, CommandError
from courses.models import Course, Category, SubCategory

class Command(BaseCommand):

    def handle(self, *args, **options):
    	_cats = ['Computer Science', 'Arts & Design', 'Data Science', 'Business', 'Finance & Accounting', 'Health & Fitness', 'IT & Software', 'Lifestyle', 'Marketing', 'Music', 'Office Productivity', 'Personal Development', 'Photography', 'Teaching & Academics',]

    	for i in range(len(_cats)):
    		print(_cats[i])
    		cat = Category.objects.filter(title=_cats[i])
    		print(cat,'hhh')
    		if cat:
	    		courses = Course.objects.filter(category=cat[0])
	    		for j in range(len(courses)):
	    			sub_cat = SubCategory.objects.filter(course__title=courses[j].title)
	    			for k in range(len(sub_cat)):
	    				SubCategory.objects.filter(title=sub_cat[k].title).update(category=cat[0])

    	return 'success'