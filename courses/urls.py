from django.conf.urls import url

from .views import (
		HomePageView,
		HomePageAPIView,
		AllCourseListView,
		SubcategoryListView,
		CourseListView,
		CourseDetailView,
		SearchListView,

		udemy_api
		)

urlpatterns = [
	url(r'^udemy-api/$',udemy_api),

	url(r'^search/$', SearchListView.as_view(), name='search'),
	url(r'^$', HomePageView.as_view(), name='home'),
	url(r'^home/api/(?P<slug>[\w-]+)/$', HomePageAPIView.as_view(), name='home-api'),
	url(r'^allcourses/$', AllCourseListView.as_view(), name='all-courses'),
	url(r'^(?P<slug>[\w-]+)/(?P<slug2>[\w-]+)/$', CourseListView.as_view(), name='course-list'),
	url(r'^(?P<slug>[\w-]+)/$', SubcategoryListView.as_view(), name='subcategory-list'),
	url(r'^(?P<slug>[\w-]+)/courses/(?P<slug2>[\w-]+)/$', CourseDetailView.as_view(), name='course-detail'),
]
