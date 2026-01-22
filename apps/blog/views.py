# apps/blog/views.py
from django.shortcuts import render, get_object_or_404
from .models import Post

def index(request): # <--- Le nom doit être identique à celui dans urls.py
    posts = Post.objects.filter(published=True).order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})

def detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, published=True)
    return render(request, 'blog/blog_detail.html', {'post': post})