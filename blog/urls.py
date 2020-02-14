from django.urls import include, path

from blog import views


app_name = 'blog'


urlpatterns = [
    path('create/', views.PostCreateView.as_view(), name='create'),
    path('<slug>/', views.PostDetailView.as_view(), name='detail'),
    path('update/<slug>/', views.PostUpdateView.as_view(), name='update'),
    path('', views.PostListView.as_view(), name='list'),
    path('category/<slug>/', views.CategoryPostListView.as_view(), name='category-posts'),
]


