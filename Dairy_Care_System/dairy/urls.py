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
    path('productexplore',views.productexplore,name='productexplore'),
    path('forgotpassword',views.forgotpassword,name='forgotpassword'),
    path('resetpassword/<str:token>/', views.resetpassword, name='resetpassword'),
    path('logout', views.logout, name='logout'),

    path('changepassword/', views.changepassword, name='changepassword'),
    path('userprofile',views.userprofile,name='userprofile'),
    path('updateuserprofile',views.updateuserprofile,name='updateuserprofile'),
    # path('send-otp/', views.send_otp, name='send_otp'),
    # path('verify-otp/', views.verify_otp, name='verify_otp'),


    path('adminpage',views.adminpage,name='adminpage'),
    path('adminproductslist',views.adminproductslist,name='adminproductslist'),
    path('adminanimalslist',views.adminanimalslist,name='adminanimalslist'),
    path('deliveryassigns', views.deliveryassigns, name='deliveryassigns'),
    path('addemployee', views.addemployee, name='addemployee'),
    path('adminmilkdetails/', views.adminmilkdetails, name='adminmilkdetails'),
    path('adminproductstock',views.adminproductstock,name='adminproductstock'),
    path('adminfeedbackreview',views.adminfeedbackreview,name='adminfeedbackreview'),
    path('adminstocknotification', views.adminstocknotification, name='adminstocknotification'),
    path('reguserlist/<str:role>/',views.reguserlist,name='reguserlist'),
    path('regdeleteuser/<int:user_id>/',views.regdeleteuser, name='regdeleteuser'),
    path('restoreuser/<int:user_id>/',views.restoreuser, name='restoreuser'),
    path('deleteaccount/<int:user_id>/',views.deleteaccount, name='deleteaccount'),


    path('farmownerpage', views.farmownerpage, name='farmownerpage'),
    path('feedbackreview',views.feedbackreview,name='feedbackreview'),
    path('diseasedetection',views.diseasedetection,name='diseasedetection'),

    path('addproducts',views.addproducts,name='addproducts'),
    path('editproduct', views.editproduct, name='editproduct'),
    path('updateproduct/<int:product_id>/', views.updateproduct, name='updateproduct'),
    path('deleteproduct/<int:product_id>/',views.deleteproduct, name='deleteproduct'),
    path('restoreproduct/<int:product_id>/',views.restoreproduct, name='restoreproduct'),
    path('productslist',views.productslist,name='productslist'),
    path('productstock',views.productstock,name='productstock'),
    path('preorderfarm',views.preorderfarm,name='preorderfarm'),
    path('orderdetails',views.orderdetails,name='orderdetails'),
    path('stocknotification', views.stocknotification, name='stocknotification'),
    path('farmerproductstock',views.farmerproductstock,name='farmerproductstock'),
    path('salegraph',views.salegraph,name='salegraph'),

    path('addanimal', views.addanimal, name='addanimal'),
    path('animalslist',views.animalslist,name='animalslist'),
    path('animal/<int:animal_id>/', views.animaldetails, name='animaldetails'),
    path('updateanimal/<int:animal_id>/', views.updateanimal, name='updateanimal'),
    path('animal/<int:animal_id>/animalhealthstatus/', views.animal_health_status, name='animal_health_status'),
    path('animal/<int:animal_id>/health/add/', views.add_health_record, name='add_health_record'),
    path('health/update/<int:health_id>/', views.update_health_record, name='update_health_record'),
    path('animal/delete/<int:animal_id>/', views.delete_animal, name='delete_animal'),
    path('animal/restore/<int:animal_id>/', views.restore_animal, name='restore_animal'),
    path('milkdetails/', views.milkdetails, name='milkdetails'),


    path('customerpage',views.customerpage,name='customerpage'),
    path('chatbot-response/', views.chatbot_response, name='chatbot_response'),
    path('feedbackpage',views.feedbackpage,name='feedbackpage'),
    path('custproductslist',views.custproductslist,name='custproductslist'),
    path('image-search/', views.image_search, name='image_search'),
    path('productdetails/', views.productdetails, name='productdetails'),
    path('custfeedback',views.custfeedback,name='custfeedback'),
    path('wishlist', views.wishlist, name='wishlist'),
    path('preorder/', views.preorder, name='preorder'),
    path('preorderlisting', views.preorderlisting, name='preorderlisting'),  # URL for pre-order list
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('viewcart', views.viewcart, name='viewcart'),
    path('cart/update/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('cart/delete/<int:cart_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('checkoutbilling/', views.checkoutbilling, name='checkoutbilling'),
    path('checkoutorder/', views.checkoutorder, name='checkoutorder'),
    path('ordersummary/<int:order_id>/', views.ordersummary, name='ordersummary'),
    path('orderfullsum/<int:order_id>/', views.orderfullsum, name='orderfullsum'),
    path('orderhistory/', views.orderhistory, name='orderhistory'),
    path('pendingorders/', views.pendingorders, name='pendingorders'),
    path('cancelorder/<int:order_id>/', views.cancelorder, name='cancelorder'),


    path('employeepage',views.employeepage,name='employeepage'),
    path('deliverydetailsall', views.deliverydetailsall, name='deliverydetailsall'),
    path('get_employees/', views.get_employees, name='get_employees'),
    path('assign_delivery/', views.assign_delivery, name='assign_delivery'),
    path('deliveryboyassigns', views.deliveryboyassigns, name='deliveryboyassigns'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('get_order_tracking/<int:order_id>/', views.get_order_tracking, name='get_order_tracking'),
    path('validate_dairy_image/', views.validate_dairy_image, name='validate_dairy_image'),
    path('deliverynotifications', views.deliverynotifications, name='deliverynotifications'),

    path('generate_qr/<int:order_id>/', views.generate_qr_code, name='generate_qr_code'),
    path('verify_qr/<int:order_id>/', views.verify_qr, name='verify_qr'),
    path("confirm-delivery/<int:order_id>/", views.confirm_delivery, name="confirm_delivery"),
    path('scan-qr/', views.scan_qr, name='scan_qr'),

    path('get_delivery_status/<int:order_id>/', views.get_delivery_status, name='get_delivery_status'),

    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    
# path('productslist/<int:product_id>/',views.productdetails, name='productdetails'),
    
#     path('wishlist', views.wishlist, name='wishlist'),
#     path('addwishlist/<int:product_id>/', views.addwishlist, name='addwishlist'),
#     path('removewishlist/<int:item_id>/', views.removewishlist, name='removewishlist'),
     
