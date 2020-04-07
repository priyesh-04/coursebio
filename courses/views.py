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
		context['popular_course_list'] = Course.objects.filter(popular=True).distinct()
		# print(context,'con')
		return context



class AllCourseListView(ListView):
	model = Course
	template_name = 'courses/course_list.html'
		


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
		context['related_courses'] = related_courses.exclude(title=course.title)
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