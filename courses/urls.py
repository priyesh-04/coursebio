from django.conf.urls import url

from .views import (
		HomePageView,
		SubcategoryListView,
		CourseListView,
		CourseDetailView,
		SearchListView,
		)

urlpatterns = [
	url(r'^search$', SearchListView.as_view(), name='search'),
	url(r'^$', HomePageView.as_view(), name='home'),
	url(r'^(?P<slug>[\w-]+)/(?P<slug2>[\w-]+)/$', CourseListView.as_view(), name='course-list'),
	url(r'^(?P<slug>[\w-]+)/$', SubcategoryListView.as_view(), name='subcategory-list'),
	url(r'^(?P<slug>[\w-]+)/courses/(?P<slug2>[\w-]+)/$', CourseDetailView.as_view(), name='course-detail'),
	# url(r'^(?P<slug>[\w-]+)/list$', ProductListView.as_view(), name='product-list'),
]
