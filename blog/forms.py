from django import forms

from blog.models import Post

from pagedown.widgets import AdminPagedownWidget, PagedownWidget


# Admin forms

class AdminPostForm(forms.ModelForm):
    content = forms.CharField(widget=AdminPagedownWidget())

    class Meta:
        model = Post
        fields = '__all__'


# General forms


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget())
    publish = forms.DateField(widget=forms.SelectDateWidget)
    class Meta:
        model = Post
        fields = '__all__'
        # fields = [
        #     "title",
        #     "content",
        #     "image",
        #     "draft",
        #     "publish",
        # ]