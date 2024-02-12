from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

    
urlpatterns = [
    # Post 
    path('change_status/<int:id>/', views.UpdateStatusView.as_view(), name='update_status'),


    path('post-idea/', views.AdminAllPost.as_view(), name='admin_all_post'),
    path('create-post/',views.CreatePost.as_view(), name="create_post"),
    path('post/', views.AllPost.as_view(), name='all_post'),
    path('post/view/<str:id>', views.PostView.as_view(), name='post'),
    path('post/edit/<str:id>/', views.EditPost.as_view(), name='edit_post'),
    path('post/delete/<str:id>/', views.DeletePost.as_view(), name="delete_post"),
    # Author
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name='dashboard/user/reset_password.html',
            email_template_name='dashboard/user/password_reset_email.txt',
            subject_template_name='dashboard/user/password_reset_subject.txt'),name="reset_password"),
    path('reset_password_send/',auth_views.PasswordResetDoneView.as_view(template_name='dashboard/user/password_reset_done.html'),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='dashboard/user/password_reset_confirm.html'),name="password_reset_confirm"),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/user/password_reset_complete.html'),name="password_reset_complete"),
    
    path('dashboard/user/all_user/', views.AllUserView.as_view(), name='all_user'),

    path('user/delete_user/<int:pk>/', views.DeleteUserView.as_view(), name='delete_user'),
    path('profile/',views.AuthorProfile.as_view(), name='profile'),
    path('profile/edit/', views.EditAuthor.as_view(), name="edit"),
    
]
