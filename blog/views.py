from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from django.views.generic import (CreateView,
								  DetailView,
								  ListView,
								  UpdateView,
								)
from django.http import Http404
from django.shortcuts import get_object_or_404
from blog.models import BlogCategory, Post
from django.core.paginator import Paginator

from blog.mixins import AccessMixin
from blog.forms import PostForm
# Create your views here.

def blog_category_list(request):
    # BlogCategory loops on index page.
    category_list = BlogCategory.objects.filter()
    context = {

        "blog_category_list": category_list,
    }
    return context


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, *args, **kwargs):
        context = super(PostDetailView, self).get_context_data(*args, **kwargs)
        slug = self.kwargs.get("slug")
        instance = get_object_or_404(Post, slug=slug)
        if instance.publish > timezone.now().date() or instance.draft:
            if not self.request.user.is_staff or not self.request.user.is_superuser:
                raise Http404
        qs = Post.objects.active().filter(slug=slug)
        if qs:
            reading_post = qs[0]
        # print(reading_post)
            category = reading_post.category
            related_articles = Post.objects.active().filter(category=category)
            recent_articles = Post.objects.active().filter(category=category).order_by('-publish')[:7]
            context['recent_articles'] = related_articles.exclude(title=reading_post.title)
            context['related_articles'] = related_articles.exclude(title=reading_post.title)
        print(context,'DetailView')
        return context


class PostListView(ListView):
    model = Post
    paginate_by = 8

    def get_queryset(self, *args, **kwargs):
        today = timezone.now().date()
        post_list = Post.objects.active() #.order_by("-timestamp")
        if self.request.user.is_staff or self.request.user.is_superuser:
            post_list = Post.objects.all()
        # print(post_list,'qs')
        return post_list

    def get_context_data(self, *args, **kwargs):
        context = super(PostListView, self).get_context_data(*args, **kwargs)
        context['page_range'] = context['paginator'].page_range
        # print(context,'ListView')
        return context


class CategoryPostListView(ListView):
    model = Post
    paginate_by = 8
    template_name = "blog/category_posts.html"

    def get_queryset(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        category = get_object_or_404(BlogCategory, slug=slug)
        qs = Post.objects.active().filter(category=category)
        if self.request.user.is_staff or self.request.user.is_superuser:
            qs = Post.objects.filter(category=category)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryPostListView, self).get_context_data(*args, **kwargs)
        slug = self.kwargs.get("slug")
        category = get_object_or_404(BlogCategory, slug=slug)
        context['category'] = category
        context['page_range'] = context['paginator'].page_range
        # print(context)
        return context


class PostCreateView(AccessMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_create.html"


class PostUpdateView(AccessMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_update.html"

    def get_context_data(self, *args, **kwargs):
        context = super(PostUpdateView, self).get_context_data(*args, **kwargs)
        context['main_img'] = context['object'].image_url
        return context


class PostSearchListView(TemplateView):
    template_name = 'blog/search_list.html'
    queryset = Post.objects.active()

    def get_context_data(self, *args, **kwargs):
        context = super(PostSearchListView, self).get_context_data(*args, **kwargs)
        qs1 = self.queryset
        query = self.request.GET.get("q", None)
        if query is not None:
            qs2 = qs1.filter(
                        Q(title__icontains=query)
                        |Q(content__icontains=query)
                        | Q(category__title__icontains=query) 
                        | Q(tag__title__icontains=query)
                        )
            context['post_list'] = qs2
            context['query'] = query
            # print(context['query'],'query')
        return context