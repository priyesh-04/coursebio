from django.db.models import Q
from django.shortcuts import render
from django.views.generic.base import TemplateView
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
        slug = self.kwargs.get("slug")
        qs = Post.objects.filter(slug=slug)
        reading_post = qs[0]
        print(reading_post)
        category = reading_post.category
        related_articles = Post.objects.filter(category=category)
        context['related_articles'] = related_articles.exclude(title=reading_post.title)
        # print(context)
        return context


class PostListView(ListView):
    model = Post
    paginate_by = 3

    def get_context_data(self, *args, **kwargs):
        context = super(PostListView, self).get_context_data(*args, **kwargs)
        # context['product_list'] = Product.objects.all()
        # context['image_list'] = Images.objects.filter(is_main_image=True)
        # context['page_range'] = context['paginator'].page_range
        # print(context['post_list'].values())
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
        # print(context)
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
        context['main_img'] = context['object'].image_url
        return context


class PostSearchListView(TemplateView):
    template_name = 'blog/search_list.html'
    queryset = Post.objects.all()

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