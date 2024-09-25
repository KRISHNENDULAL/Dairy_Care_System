from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('reguserlist/<str:role>/',views.reguserlist,name='reguserlist'),
    path('regdeleteuser/<int:user_id>/',views.regdeleteuser, name='regdeleteuser'),
    path('restoreuser/<int:user_id>/',views.restoreuser, name='restoreuser'),
    path('changepassword/', views.changepassword, name='changepassword'),
    path('customerpage',views.customerpage,name='customerpage'),
    path('employeepage',views.employeepage,name='employeepage'),
    path('logout', views.user_logout, name='logout'),
    path('feedbackpage',views.feedbackpage,name='feedbackpage'),
    path('userprofile',views.userprofile,name='userprofile'),
    path('updateuserprofile',views.updateuserprofile,name='updateuserprofile'),
    path('productslist',views.productslist,name='productslist'),
    path('custproductslist',views.custproductslist,name='custproductslist'),
    path('productslist/<int:product_id>/',views.productdetails, name='productdetails'),
    path('addproducts',views.addproducts,name='addproducts'),
    path('editproduct', views.editproduct, name='editproduct'),
    path('deleteproduct/<int:product_id>/',views.deleteproduct, name='deleteproduct'),
    path('restoreproduct/<int:product_id>/',views.restoreproduct, name='restoreproduct')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    

     
