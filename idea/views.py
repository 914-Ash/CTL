import idea
from django.shortcuts import render,get_object_or_404
from django.views import View
from .models import Idea
from django.core.paginator import Paginator
from django.core.paginator import Paginator
from django.db.models import Q


class HomeView(View):
    def get(self, request, *args, **kwargs):
        # Fetch the latest posts and featured posts with status="active"
        latest_posts = Idea.objects.filter(status='商品化').order_by('-created_at')[:5]

        # Pagination for home page
        all_posts = Idea.objects.filter(status='商品化').order_by('-created_at')
        paginator = Paginator(all_posts, 10)  # Show 10 posts per page
        page_number = request.GET.get('page')
        posts = paginator.get_page(page_number)

        context = {
            'latest_posts': latest_posts,
            'posts': posts,
        }
        return render(request, 'home/index.html', context)



class SearchView(View):
    def get(self,request,*args,**kwargs):
        search = request.GET['q']
        post = Idea.objects.filter(status='商品化')
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
