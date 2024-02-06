import idea
from django import views
from django.core import paginator
from django.http import HttpResponseRedirect
from django.db.models.fields import EmailField
from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from .models import Idea, Tag
from django.core.paginator import Paginator
from django.db.models import Count 
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q


class HomeView(View):
    def get(self, request, *args, **kwargs):
        # Fetch the latest posts and featured posts with status="active"
        latest_posts = Idea.objects.filter(status='active').order_by('-created_at')[:5]
        featured_posts = Idea.objects.filter(status='active', featured=True).order_by('-created_at')[:5]

        # Pagination for home page
        all_posts = Idea.objects.filter(status='active').order_by('-created_at')
        paginator = Paginator(all_posts, 10)  # Show 10 posts per page
        page_number = request.GET.get('page')
        posts = paginator.get_page(page_number)

        context = {
            'latest_posts': latest_posts,
            'featured_posts': featured_posts,
            'posts': posts,
        }
        return render(request, 'home/index.html', context)

# tag View
class TagView(View):
    def get(self,request,id,*args,**kwargs):
        tag_obj = get_object_or_404(Tag, id=id)
        post = tag_obj.idea_set.all().order_by('-id')
        tag_count = post.count()
        context={
            'tag':tag_obj,
            'post':post,
            'tag_count':tag_count
        }
        return render(request,'home/tag.html',context)

class SearchView(View):
    def get(self,request,*args,**kwargs):
        search = request.GET['q']
        post = Idea.objects.filter(status='active')
        if len(search) > 100:
            posts = post.none()
        else:
            posts = post.filter(
                Q(title__icontains=search) |
                Q(detail__icontains = search)
                
            )
        context ={
            'post':posts,
            'search':search
        }
        return render(request,'home/search.html', context)
