from django.conf.urls import url

from .views import (
		HomePageView,
		SubcategoryListView,
		)

urlpatterns = [
	# url(r'^search$', SearchListView.as_view(), name='search-view'),
	url(r'^$', HomePageView.as_view(), name='home'),
	# url(r'^create/$', post, name='create-product'),
	url(r'^(?P<slug>[\w-]+)/$', SubcategoryListView.as_view(), name='subcategory-list'),
	# url(r'^(?P<slug>[\w-]+)/list$', ProductListView.as_view(), name='product-list'),
	# url(r'^(?P<slug>[\w-]+)/(?P<slug2>[\w-]+)/$', BrandProductListView.as_view(), name='brand-product-list'),
	# url(r'^(?P<slug>[\w-]+)/(?P<slug2>[\w-]+)/(?P<slug3>[\w-]+)/$', ProductDetailView.as_view(), name='product-detail'),
]
