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

from courses.models import (
								Category,
							 	SubCategory, 
							 	Course, 
							 	Provider
							)
# Create your views here.

def product_category_list(request):
    # Category loops on index page.
    category_list = Category.objects.filter()
    context = {
        "product_category_list": category_list,
    }
    return context


class HomePageView(ListView):
	model = Course
	# context_object_name = 'product_list'
	template_name = 'home.html'

	# def get_queryset(self, *args, **kwargs):
	# 	qs = Course.objects.all()
	# 	return qs

	def get_context_data(self, *args, **kwargs):
		context = super(HomePageView, self).get_context_data(*args, **kwargs)
		context['category_list'] = Category.objects.all()
		# context['image_list'] = Images.objects.filter(is_main_image=True)
		# print(context,'con')
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
		# context['image_list'] = Images.objects.filter(is_main_image=True)
		print(context,'con')
		return context
