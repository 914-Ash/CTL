from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from django.views.generic.edit import DeleteView
from idea.models import Idea, Tag
from product.models import Product
from .models import Author
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from django.shortcuts import render
from django.views import View


# Create Author 
class CreateAuthor(View):
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request,'dashboard/user/create_user.html')

    def post(self,request,*args,**kwargs):
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('fname')
            last_name = request.POST.get('lname')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            user = User.objects.filter(username=username,email=email,first_name=first_name,last_name=last_name)
            email_obj = Author.objects.filter(email=email)
            if user:
                messages.warning(request,'ユーザIDがすでに存在します！')
                return redirect ('create_user')
            elif password1 != password2:
                messages.warning(request,'入力された２つのパスワードが一致しない！')
                return redirect('create_user')
            else:
                auth_info={
                    'username':username,
                    'email':email,
                    'last_name':last_name,
                    'first_name':first_name,
                    'password':make_password(password1)
                }
                user = User(**auth_info)
                user.save()
            if email_obj:   
                messages.warning(request,'メールアドレスがすでに使われている!')
                return redirect('create_user')
            else:
                user_other_obj = Author(author=user, email_text=email, first_name=first_name, last_name= last_name)
                user_other_obj.save(Author)
                messages.success(request,'ご登録いただきありがとうございます ログインしてください')
                return redirect('login')

# Author Profile
class AuthorProfile(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)

    def get(self, request):
        author = request.user
        user = request.user.author
        post = user.idea_set.all().order_by('-id')
        context= {
            'author':author,
            'post':post
        } 
        return render(request,'dashboard/user/profile.html', context)

class EditAuthor(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'dashboard/user/edit_profile.html')

    def post(self, request):
        user = request.user
        obj = request.user.author

        # Handle file upload
        obj.author_image = request.FILES.get('image', obj.author_image)

        # Update other fields
        obj.first_name = request.POST.get('fname', obj.first_name)
        obj.last_name = request.POST.get('lname', obj.last_name)
        obj.email = request.POST.get('email', obj.email)
        obj.save()

        # Handle checkbox for active status
        user.is_active = 'active' in request.POST

        user.save()

        messages.success(request, 'あなたのプロファイルが正常に更新されました')
        return redirect('profile')
    

class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'dashboard/user/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # User does not exist, show a warning message
            messages.warning(request, 'ユーザIDかパスワードが間違っています。')
            return redirect('login')

        # Check the password manually
        if user.check_password(password):
            # User exists, check if active
            if not user.is_active:
                self.send_activation_email(request, user)
                # Activate the user
                messages.warning(request, 'アカウントが停止中です。再開する場合メールアドレスに届いてあるメールを確認してください。')
                return redirect('login')

            # Log in the user
            login(request, user)
            return redirect('home')
        else:
            # Password does not match, show a warning message
            messages.warning(request, 'ユーザIDかパスワードが間違っています。')
            return redirect('login')

    def send_activation_email(self, request, user):
        # Generate activation token
        token = default_token_generator.make_token(user)
        
        # Build activation URL
        activation_url = request.build_absolute_uri(
            reverse('activate', args=[urlsafe_base64_encode(force_bytes(user.pk)), token])
        )

        # Send activation email
        subject = 'アカウントの再開'
        message = f'下記のリンクを押してアカウントの再開する:\n\n{activation_url}'
        from_email = 'your_email@example.com'  # Replace with your email
        to_email = user.email
        send_mail(subject, message, from_email, [to_email])

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # Activate the user
            user.is_active = True
            user.save()
            messages.success(request, 'アカウントの再開に成功。またログインできるようになりました。')
        else:
            messages.error(request, '無効なリンク。')

        return redirect('login')

# Logout View
class LogoutView(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)

    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('home')




# Tag functions
class TagFunction(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)

    def get(self, request):
        tag_obj = Tag.objects.all().order_by('-id')
        context = {
            'tag':tag_obj
        }   
        return render (request,'dashboard/tag/tag.html', context)
        
# add Tags
class AddTag(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)

    def get(self,request):
        return render(request,'dashboard/tag/tag.html')

    def post(self,request):
        if request.method == 'POST':
            tag= request.POST.get('tag')
            obj = Tag.objects.create(name=tag)
            obj.save()
            return redirect('tag')

# update Tags
class UpdateTag(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)

    def post(self,request, id):
        obj = get_object_or_404(Tag, id=id)
        obj.name = request.POST.get('tag')
        obj.save()
        return redirect('tag')

# Delete Tags
class DeleteTag(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)

    def post(self, request, id):
        obj = get_object_or_404(Tag, id=id)
        obj.delete() 
        return redirect('tag') 

# Post Lists 
# Create Post
class CreatePost(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)
    
    def get(self,request):
        return render(request,'dashboard/post/create_post.html')

    def post(self,request):
        author = request.user.author
        title = request.POST.get('title')
        detail = request.POST.get('detail')
        image = request.FILES.get('image')

        post_obj = Idea(author=author,title=title, detail=detail,image=image)
        post_obj.save(post_obj)
        messages.success(request,'アイディアを投稿しました')
        return redirect('all_post')

# All Post show

class AllPost(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)
    
    def get(self,request):
        user = request.user.author
        post = user.idea_set.all().order_by('-id')
        context = {
            'post':post
        }
        return render(request,'dashboard/post/all_post.html',context)

# Post detail 
class PostView(View):
    def dispatch(self, request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)
    
    def get(self, request,id):
        post_obj = get_object_or_404(Idea, id=id)
        context={
            'post':post_obj
        }
        return render(request,'dashboard/post/post_view.html', context)


        
class EditPost(View):
    @method_decorator(login_required(login_url='login'))   
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id):
        obj = get_object_or_404(Idea, id=id)
        return render(request, 'dashboard/post/edit_post.html', {'obj': obj})

    def post(self, request, id):
        obj = get_object_or_404(Idea, id=id)
        obj.title = request.POST.get('title')
        obj.detail = request.POST.get('detail')
        obj.image = request.FILES.get('image')
        obj.save()
        messages.success(request, 'アイディアを更新しました。')
        return redirect('all_post')



# Delete Posts
class DeletePost(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)
    

    def post(self, request,id):
        obj = get_object_or_404(Idea, id=id)
        obj.delete()
        messages.success(request,'アイディアを削除しました。')
        # Redirect To the Same Page
        return redirect('all_post')
    

class AdminAllPost(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        # Get all ideas from all authors
        all_posts = Idea.objects.all().order_by('-id')

        context = {
            'all_posts': all_posts
        }

        return render(request, 'dashboard/post/admin_all_post.html', context)

from django.db import IntegrityError

class UpdateStatusView(View):
    def post(self, request, id):
        idea = get_object_or_404(Idea, id=id)
        new_status = request.POST.get('status')

        # Perform validation and update status as needed
        idea.status = new_status
        idea.save()

        # Check if the status is changed to 'active'
        if new_status == 'active':
            try:
                # Try to get an existing product associated with the idea
                product = Product.objects.get(title=idea.title, author=idea.author)
            except Product.DoesNotExist:
                # If no existing product, create a new one
                product = Product(
                    title=idea.title,
                    description=idea.detail,
                    image=idea.image,
                    status=idea.status,
                    author=idea.author,
                )
            else:
                # Update the existing product
                product.description = idea.detail
                product.image = idea.image
                product.status = idea.status

            try:
                # Save the product (either the new one or the updated existing one)
                product.save()
                # Update the tags using set() method
                product.tags.set(idea.tags.all())
            except IntegrityError as e:
                # Handle IntegrityError if needed (e.g., unique constraint violation)
                print(f"IntegrityError: {e}")
        elif new_status == 'pending':
            # Check if there is an associated product and delete it
            try:
                product = Product.objects.get(title=idea.title, author=idea.author)
                product.delete()
            except Product.DoesNotExist:
                pass  # No product to delete

        # Redirect back to the page or wherever you want
        return redirect('admin_all_post')

class DeleteUserView(DeleteView):
    model = User
    template_name = 'dashboard/user/delete_user.html'
    success_url = reverse_lazy('all_user')

    def delete(self, request, *args, **kwargs):
        # Delete the User instance using the parent class method
        response = super().delete(request, *args, **kwargs)

        messages.success(request, 'User deleted successfully.')

        return response


class AllUserView(View):
    template_name = 'dashboard/user/all_user.html'

    def get(self, request):
        # Get all users
        all_users = User.objects.all().order_by('-id')

        context = {
            'all_users': all_users
        }

        return render(request, self.template_name, context)