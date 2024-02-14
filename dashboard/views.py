from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from django.views.generic.edit import DeleteView
from idea.models import Idea, IdeaFile
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
from django.core.mail import send_mail
from django.shortcuts import render
from django.views import View
from django.utils import timezone


# Create Author 
class CreateAuthor(View):
    template_name = 'dashboard/user/create_user.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validation
        if User.objects.filter(username=username).exists():
            messages.warning(request, 'ユーザIDがすでに存在します！')
            return redirect('create_user')

        if User.objects.filter(email=email).exists():
            messages.warning(request, 'メールアドレスがすでに使用されています！')
            return redirect('create_user')
        
        if password1 != password2:
            messages.warning(request, '入力された２つのパスワードが一致しません！')
            return redirect('create_user')

        # Create User
        user = User(username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password1)
        user.save()

        # Create Author
        author = Author(author=user, email_text=email, first_name=first_name, last_name=last_name)
        author.save()

        messages.success(request, 'ご登録いただきありがとうございます。ログインしてください。')
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
    @method_decorator(login_required(login_url='login'), name='dispatch')
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
        new_email = request.POST.get('email', user.email)

        # Check if the new email is already registered by another user
        if new_email != user.email and User.objects.filter(email=new_email).exists():
            messages.error(request, 'このメールアドレスがすでに使われています。')
            return redirect('edit')

        user.email = new_email
        user.save()
        obj.email_text = new_email 

        obj.save()  # Save the Author object

        messages.success(request, 'プロフィールを更新しました。')
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
            messages.warning(request, 'ユーザが存在しません。')
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



# Logout View
class LogoutView(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request,*args,**kwargs)

    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('home')
 

# Post Lists 
# Create Post
class CreatePost(View):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'dashboard/post/create_post.html')

    def post(self, request):
        author = request.user.author
        email_text = author.email_text
        title = request.POST.get('title')
        detail = request.POST.get('detail')
        image = request.FILES.get('image')

        # Create the Idea object
        post_obj = Idea.objects.create(author=author, email_text=email_text, title=title, detail=detail, image=image)

        # Handle file uploads
        files = request.FILES.getlist('files')

        for file in files:
        # Create IdeaFile instance
            idea_file = IdeaFile.objects.create(idea=post_obj, file=file)
        # Add IdeaFile instance to the many-to-many relationship
            post_obj.files.add(idea_file)

        messages.success(request, 'アイディアを投稿しました')
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
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id):
        post_obj = get_object_or_404(Idea, id=id)
        files = post_obj.files.all()  # Fetch associated files
        context = {
            'post': post_obj,
            'files': files,  # Include files in the context
        }
        return render(request, 'dashboard/post/post_view.html', context)
    

        
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

        # Check if a new image is provided
        new_image = request.FILES.get('image')
        if new_image:
            obj.image = new_image

        # Handle file updates
        new_files = request.FILES.getlist('files')

        # Clear existing files associated with the Idea object
        if new_files:
            obj.files.clear()

            for file in new_files:
                # Create IdeaFile instance
                idea_file = IdeaFile.objects.create(idea=obj, file=file)
                # Add IdeaFile instance to the many-to-many relationship
                obj.files.add(idea_file)

            obj.save()
            messages.success(request, 'アイディアを更新しました。')
            return redirect('all_post')
        else:
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
        if new_status in ['商品化', '保留']:
            idea.status = new_status
            idea.new_date_field = timezone.now()  # Add a new date field to your model
            idea.save()

        # Check if the status is changed to 'active'
        return redirect('admin_all_post')


from django.http import HttpResponseRedirect, HttpResponseForbidden
class DeleteUserView(DeleteView):
    model = User

    def get_success_url(self):
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return reverse_lazy('all_user')
        else:
            return reverse_lazy('login')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        messages.success(request, 'ユーザの削除に成功。')
        self.object.delete()
        return HttpResponseRedirect(success_url)



class AllUserView(View):
    template_name = 'dashboard/user/all_user.html'

    def get(self, request):
        # Check if the user is authenticated and a staff member
        if not request.user.is_authenticated or not request.user.is_staff:
            # Redirect to the login page if not authenticated or not a staff member
            return redirect('login')

        # Get all users
        all_users = User.objects.all().order_by('-id')

        context = {
            'all_users': all_users
        }

        return render(request, self.template_name, context)

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST['email']
        # Check if the email exists in the database
        if User.objects.filter(email=email).exists():
            # The email is registered, proceed with sending the reset link
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                # Your password reset logic here
                # Send the reset link and redirect to success page
                return redirect('password_reset_done')
        else:
            # The email is not registered, show an error message
            messages.error(request, 'メールアドレスが登録されていません。')
            return render(request, 'dashboard/user/reset_password.html')
    else:
        form = PasswordResetForm()
        return render(request, 'dashboard/user/reset_password.html', {'form': form})
