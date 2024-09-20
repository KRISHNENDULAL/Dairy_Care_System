from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home,name='home'),
    path('login', views.login,name='login'),
    path('registration', views.registration,name='registration'),
    path('about', views.about,name='about'),
    path('contactus', views.contactus,name='contactus'),
    path('forgotpassword',views.forgotpassword,name='forgotpassword'),
    path('resetpassword/<str:token>/', views.resetpassword, name='resetpassword'),
    path('adminpage',views.adminpage,name='adminpage'),
    path('addemployee', views.addemployee, name='addemployee'),
    path('changepassword/', views.changepassword, name='changepassword'),
    path('customerpage',views.customerpage,name='customerpage'),
    path('employeepage',views.employeepage,name='employeepage'),
    path('logout', views.user_logout, name='logout'),
    path('feedbackpage',views.feedbackpage,name='feedbackpage'),
    path('userprofile',views.userprofile,name='userprofile')
] 

