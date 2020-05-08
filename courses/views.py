from django.db.models import Q
from django.http import  (HttpResponseRedirect, 
						  HttpResponse, 
						  JsonResponse
						)

from django.views.generic.base import TemplateView

from django.views.generic import (ListView, 
								  DetailView
								)

from django.shortcuts import get_object_or_404

from tags.models import Tag
from courses.models import (
								Category,
							 	SubCategory, 
							 	Course, 
							 	Provider
							)

def course_category_list(request):
    # Category loops on index page.
    category_list = Category.objects.all()
    context = {
        "course_category_list": category_list,
    }
    return context

def course_provider_list(request):
    course_provider_list = Provider.objects.all()
    context = {
        "course_provider_list": course_provider_list,
    }
    return context


def all_courses_list(request):
	all_courses_list = Course.objects.all()
	context = {
		"all_courses_list": all_courses_list,
	}
	return context



from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .serializers import CourseModelSerializer, CategoryModelSerializer

class HomePageAPIView(ListAPIView):
	serializer_class = CourseModelSerializer

	def get_queryset(self, slug=None, *args, **kwargs):
		slug = self.kwargs.get("slug")
		print(slug,'slug')
		category = get_object_or_404(Category, slug=slug)
		print(category,'category')
		url_ = category.get_absolute_url()
		print(url_,'url_')
		qs = Course.objects.filter(category=category)
		data = {
		    "qs": qs,
		}
		print(qs[0].provider.image_url,'qs')
		return qs



class HomePageView(ListView):
	model = Course
	# context_object_name = 'course_list'
	template_name = 'home.html'

	# def get_queryset(self, *args, **kwargs):
	# 	qs = Course.objects.all()
	# 	return qs

	def get_context_data(self, *args, **kwargs):
		context = super(HomePageView, self).get_context_data(*args, **kwargs)
		context['category_list'] = Category.objects.all()
		context['popular_course_list'] = Course.objects.filter(popular=True).distinct().order_by("?")[:10]
		# print(context,'con')
		return context

from .udemy import Udemy
from accounts.models import MyUser
class AllCourseListView(ListView):
	model = Course
	template_name = 'courses/course_list.html'

	def get_context_data(self, *args, **kwargs):
		context = super(AllCourseListView, self).get_context_data(*args, **kwargs)
		
		user 		= MyUser.objects.get(email='priyesh.shukla070@gmail.com')
		provider 	= Provider.objects.get(title='udemy')

		udemy = Udemy('A3NMCg6nzLUPjTYR2bIjYeU9cUW1k3wHRQyzTX03', '9PPNGtZy0SPqcLn2mfIltOFzOkqzPQRInEmlLQAtscDkEjadVCO0wwc1Cu2qxMwt4ZlhlMcUZibyIrRx45pWeJmb7KJK4bCt6HgGAolEXDZA94VRpUmkYxWTFMbhB69f')
		udemy_cats = ['Development', 'Design', 'Business', 'Finance & Accounting', 'Health & Fitness', 'IT & Software', 'Lifestyle', 'Marketing', 'Music', 'Office Productivity', 'Personal Development', 'Photography', 'Teaching & Academics', 'Udemy Free Resource Center']

		my_cat_dict = {'Development':'Computer Science', 'Design':'Arts & Design', 'Business':'Business', 'Finance & Accounting':'Finance & Accounting', 'Health & Fitness':'Health & Fitness', 'IT & Software':'IT & Software', 'Lifestyle':'Lifestyle', 'Marketing':'Marketing', 'Music':'Music', 'Office Productivity':'Office Productivity', 'Personal Development':'Personal Development', 'Photography':'Photography', 'Teaching & Academics':'Teaching & Academics', 'Udemy Free Resource Center':'Others', }

		for cats in range(len(udemy_cats)):
			for i in range(1,3):
				udemy_course_list = udemy.courses(page=1, page_size=3,category=udemy_cats[cats])
				print(udemy_course_list,'list')
				for i in range(len(udemy_course_list['results'])):
					
					udemy_course_detail = udemy.course_detail(udemy_course_list['results'][i]['id'], course ='@all')
					course_ = Course.objects.filter(title=udemy_course_detail['title'])
					print('Detail',udemy_course_detail,'Detail')
					if course_:
						i=i+1
						continue
					
					elif not course_:
						print('Total',i,'courses added in database.')
						category = Category.objects.get(title=my_cat_dict[udemy_cats[cats]])
						video = udemy_course_detail['promo_asset']['download_urls']['Video'][0]['file']
						image = udemy_course_detail['image_480x270']
						author = udemy_course_detail['visible_instructors'][0]['title']
						duration = udemy_course_detail['content_info']
						level = udemy_course_detail['instructional_level']
						url = 'https://www.udemy.com/' + udemy_course_detail['url']
						course_obj = Course(user=user, category=category, provider=provider,image_url=image,video_url=video, title=udemy_course_detail['title'],description=udemy_course_detail['description'],author=author,duration=duration,level=level,course_url=url)
						if udemy_course_detail['is_paid']:
							course_obj.price = 13.0
						else:
							course_obj.is_free=True
						course_obj.certificate = True
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

		return context	


class SubcategoryListView(ListView):
	model = SubCategory

	def get_context_data(self, *args, **kwargs):
		context = super(SubcategoryListView, self).get_context_data(*args, **kwargs)
		slug = self.kwargs.get("slug")
		category = get_object_or_404(Category, slug=slug)
		context['category'] = category
		context['category_image'] = category.image_url
		context['subcategory_list'] = SubCategory.objects.filter(category=category).order_by('title')
		# print(context,'con')
		return context


class CourseListView(ListView):
	model = Course

	def get_context_data(self, *args, **kwargs):
		context = super(CourseListView, self).get_context_data(*args, **kwargs)
		slug2 = self.kwargs.get('slug2')
		subcategory = get_object_or_404(SubCategory, slug=slug2)
		context['subcategory'] = subcategory
		context['course_list'] = Course.objects.filter(subcategory=subcategory).distinct()
		# print(context,'con')
		return context


class CourseDetailView(TemplateView):
	model = Course
	template_name = 'courses/course_detail.html'

	def get_context_data(self, *args, **kwargs):
		context = super(CourseDetailView, self).get_context_data(*args, **kwargs)
		slug2 = self.kwargs.get('slug2')
		course = get_object_or_404(Course, slug=slug2)
		context['course'] = course
		context['related_tags'] = Tag.objects.filter(courses=course)
		related_courses = Course.objects.filter(category=course.category)
		context['related_courses'] = related_courses.exclude(title=course.title).order_by("?")[:10]
		# print(context['related_tags'],'con')
		return context


class SearchListView(TemplateView):
	template_name = 'courses/search_list.html'
	queryset = Course.objects.all()

	def get_context_data(self, *args, **kwargs):
		context = super(SearchListView, self).get_context_data(*args, **kwargs)
		qs1 = self.queryset
		query = self.request.GET.get("q", None)
		if query is not None:
			qs2 = qs1.filter(
						Q(title__icontains=query)
						|Q(description__icontains=query)
						|Q(author__icontains=query)
						| Q(price__icontains=query) 
						| Q(provider__title__icontains=query)
						| Q(category__title__icontains=query) 
						| Q(subcategory__title__icontains=query)
						| Q(tag__title__icontains=query)
						)
			context['course_list'] = qs2.distinct()
			context['query'] = query
			# print(context['query'],'query')
		return context