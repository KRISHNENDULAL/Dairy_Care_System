from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home,name='home'),
    path('login', views.login,name='login'),
    path('oauth/', include('social_django.urls', namespace='social')),
    
    path('regmailverify', views.regmailverify, name='regmailverify'),
    path('regotpverify', views.regotpverify, name='regotpverify'),
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
    path('logout', views.logout, name='logout'),
    path('feedbackpage',views.feedbackpage,name='feedbackpage'),
    path('feedbackreview',views.feedbackreview,name='feedbackreview'),
    path('userprofile',views.userprofile,name='userprofile'),
    path('updateuserprofile',views.updateuserprofile,name='updateuserprofile'),
    path('productslist',views.productslist,name='productslist'),
    path('productstock',views.productstock,name='productstock'),
    path('custproductslist',views.custproductslist,name='custproductslist'),

    path('productdetails/', views.productdetails, name='productdetails'),
    path('wishlist', views.wishlist, name='wishlist'),

    path('viewcart', views.viewcart, name='viewcart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('cart/delete/<int:cart_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('ordersummary/<int:order_id>/', views.ordersummary, name='ordersummary'),
    path('orderhistory/', views.orderhistory, name='orderhistory'),
    path('stocknotification', views.stocknotification, name='stocknotification'),
    path('cancelorder/<int:order_id>/', views.cancelorder, name='cancelorder'),

    path('addproducts',views.addproducts,name='addproducts'),
    path('editproduct', views.editproduct, name='editproduct'),
    path('updateproduct/<int:product_id>/', views.updateproduct, name='updateproduct'),
    path('deleteproduct/<int:product_id>/',views.deleteproduct, name='deleteproduct'),
    path('restoreproduct/<int:product_id>/',views.restoreproduct, name='restoreproduct'),
    path('animalslist',views.animalslist,name='animalslist'),
    path('addanimal', views.addanimal, name='addanimal'),
    path('animal/<int:animal_id>/', views.animaldetails, name='animaldetails'),
    path('animal/<int:animal_id>/animalhealthstatus/', views.animal_health_status, name='animal_health_status'),
    path('animal/<int:animal_id>/health/add/', views.add_health_record, name='add_health_record'),
    path('health/update/<int:health_id>/', views.update_health_record, name='update_health_record'),
    path('animal/delete/<int:animal_id>/', views.delete_animal, name='delete_animal'),
    path('animal/restore/<int:animal_id>/', views.restore_animal, name='restore_animal'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    
# path('productslist/<int:product_id>/',views.productdetails, name='productdetails'),
    
#     path('wishlist', views.wishlist, name='wishlist'),
#     path('addwishlist/<int:product_id>/', views.addwishlist, name='addwishlist'),
#     path('removewishlist/<int:item_id>/', views.removewishlist, name='removewishlist'),
     
