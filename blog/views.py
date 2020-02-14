from django.shortcuts import render
from django.views.generic import (CreateView,
								  DetailView,
								  ListView,
								  UpdateView,
								)
from django.shortcuts import get_object_or_404
from blog.models import BlogCategory, Post
from django.core.paginator import Paginator

from blog.forms import PostForm
# from products.models import Product, Images

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
        # context['related_articles'] = Post.objects.all()
        # context['product_list'] = Product.objects.all()
        # context['image_list'] = Images.objects.filter(is_main_image=True)
        return context


class PostListView(ListView):
    model = Post
    paginate_by = 3

    def get_context_data(self, *args, **kwargs):
        context = super(PostListView, self).get_context_data(*args, **kwargs)
        # context['product_list'] = Product.objects.all()
        # context['image_list'] = Images.objects.filter(is_main_image=True)
        # context['page_range'] = context['paginator'].page_range
        # print(context)
        return context


class CategoryPostListView(ListView):
    model = Post
    paginate_by = 3
    template_name = "blog/category_posts.html"

    def get_queryset(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        category = get_object_or_404(BlogCategory, slug=slug)
        qs = Post.objects.filter(category=category)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryPostListView, self).get_context_data(*args, **kwargs)
        # context['product_list'] = Product.objects.all()
        # context['image_list'] = Images.objects.filter(is_main_image=True)
        # context['page_range'] = context['paginator'].page_range
        return context


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_create.html"


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_update.html"

    def get_context_data(self, *args, **kwargs):
        context = super(PostUpdateView, self).get_context_data(*args, **kwargs)
        context['main_img'] = "http://localhost:8000" + context['object'].image.url
        return context