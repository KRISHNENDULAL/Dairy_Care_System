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
    path('regdeleteuser/DCS/', views.regdeleteuser, {'user_id': None}, name='regdeleteuser_masked'),
    path('restoreuser/<int:user_id>/',views.restoreuser, name='restoreuser'),
    path('restoreuser/DCS/', views.restoreuser, {'user_id': None}, name='restoreuser_masked'),
    path('deleteaccount/<int:user_id>/',views.deleteaccount, name='deleteaccount'),
    path('deleteaccount/DCS/', views.deleteaccount, {'user_id': None}, name='deleteaccount_masked'),


    path('farmownerpage', views.farmownerpage, name='farmownerpage'),
    path('feedbackreview',views.feedbackreview,name='feedbackreview'),
    path('diseasedetection',views.diseasedetection,name='diseasedetection'),
    path('verify-model/', views.verify_model, name='verify_model'),
    path('predict-disease/', views.predict_disease, name='predict_disease'),

    path('addproducts',views.addproducts,name='addproducts'),
    path('editproduct', views.editproduct, name='editproduct'),
    path('updateproduct/<int:product_id>/', views.updateproduct, name='updateproduct'),
    path('updateproduct/DCS/', views.updateproduct, {'product_id': None}, name='updateproduct_masked'),
    path('deleteproduct/<int:product_id>/',views.deleteproduct, name='deleteproduct'),
    path('deleteproduct/DCS/', views.deleteproduct, {'product_id': None}, name='deleteproduct_masked'),
    path('restoreproduct/<int:product_id>/',views.restoreproduct, name='restoreproduct'),
    path('restoreproduct/DCS/', views.restoreproduct, {'product_id': None}, name='restoreproduct_masked'),
    path('productslist',views.productslist,name='productslist'),
    path('productstock',views.productstock,name='productstock'),
    path('preorderfarm',views.preorderfarm,name='preorderfarm'),
    path('orderdetails',views.orderdetails,name='orderdetails'),
    path('stocknotification', views.stocknotification, name='stocknotification'),
    path('farmerproductstock',views.farmerproductstock,name='farmerproductstock'),
    path('salegraph',views.salegraph,name='salegraph'),
    path('milkqualityanalysis' ,views.milkqualityanalysis,name='milkqualityanalysis'),

    path('addanimal', views.addanimal, name='addanimal'),
    path('animalslist',views.animalslist,name='animalslist'),
    path('animal/<int:animal_id>/', views.animaldetails, name='animaldetails'),
    path('animal/DCS/', views.animaldetails, {'animal_id': 'DCS'}, name='animaldetails_masked'),
    path('updateanimal/<int:animal_id>/', views.updateanimal, name='updateanimal'),
    path('updateanimal/DCS/', views.updateanimal, {'animal_id': None}, name='updateanimal_masked'),
    path('animal/<int:animal_id>/animalhealthstatus/', views.animal_health_status, name='animal_health_status'),
    path('animal/DCS/animalhealthstatus/', views.animal_health_status, {'animal_id': 'DCS'}, name='animal_health_status_masked'),
    path('animal/<int:animal_id>/health/add/', views.add_health_record, name='add_health_record'),
    path('animal/DCS/health/add/', views.add_health_record, {'animal_id': None}, name='add_health_record_masked'),
    path('health/update/<int:health_id>/', views.update_health_record, name='update_health_record'),
    path('health/update/DCS/', views.update_health_record, {'health_id': None}, name='update_health_record_masked'),
    
    path('animal/delete/<int:animal_id>/', views.delete_animal, name='delete_animal'),
    path('animal/delete/DCS/', views.delete_animal, {'animal_id': None}, name='delete_animal_masked'),
    path('animal/restore/<int:animal_id>/', views.restore_animal, name='restore_animal'),
    path('animal/restore/DCS/', views.restore_animal, {'animal_id': None}, name='restore_animal_masked'),
    
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
    path('cart/update/DCS/', views.update_cart, {'cart_id': None}, name='update_cart_masked'),
    path('cart/delete/<int:cart_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('cart/delete/DCS/', views.delete_from_cart, {'cart_id': None}, name='delete_from_cart_masked'),
    path('checkoutbilling/', views.checkoutbilling, name='checkoutbilling'),
    path('checkoutorder/', views.checkoutorder, name='checkoutorder'),
    path('ordersummary/<int:order_id>/', views.ordersummary, name='ordersummary'),
    path('ordersummary/DCS/', views.ordersummary, {'order_id': None}, name='ordersummary_masked'),
    path('orderfullsum/<int:order_id>/', views.orderfullsum, name='orderfullsum'),
    path('orderfullsum/DCS/', views.orderfullsum, {'order_id': None}, name='orderfullsum_masked'),
    path('orderhistory/', views.orderhistory, name='orderhistory'),
    path('pendingorders/', views.pendingorders, name='pendingorders'),
    path('cancelorder/<int:order_id>/', views.cancelorder, name='cancelorder'),
    path('cancelorder/DCS/', views.cancelorder, {'order_id': None}, name='cancelorder_masked'),


    path('employeepage',views.employeepage,name='employeepage'),
    path('deliverydetailsall', views.deliverydetailsall, name='deliverydetailsall'),
    path('get_employees/', views.get_employees, name='get_employees'),
    path('assign_delivery/', views.assign_delivery, name='assign_delivery'),
    path('deliveryboyassigns', views.deliveryboyassigns, name='deliveryboyassigns'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('get_order_tracking/<int:order_id>/', views.get_order_tracking, name='get_order_tracking'),
    path('get_order_tracking/DCS/', views.get_order_tracking, {'order_id': None}, name='get_order_tracking_masked'),
    path('validate_dairy_image/', views.validate_dairy_image, name='validate_dairy_image'),
    path('deliverynotifications', views.deliverynotifications, name='deliverynotifications'),

    path('generate_qr/<int:order_id>/', views.generate_qr_code, name='generate_qr_code'),
    # path('generate_qr/DCS/', views.generate_qr_code, {'order_id': None}, name='generate_qr_code_masked'),
    path('verify_qr/<int:order_id>/', views.verify_qr, name='verify_qr'),
    # path('verify_qr/DCS/', views.verify_qr, {'order_id': None}, name='verify_qr_masked'),
    path('scan-qr/<int:order_id>/', views.scan_qr, name='scan_qr_with_id'),
    # path('scan-qr/DCS/', views.scan_qr, {'order_id': None}, name='scan_qr_masked'),
    path('scan-qr/', views.scan_qr, name='scan_qr'),
    path('confirm-delivery/<int:order_id>/', views.confirm_delivery, name='confirm_delivery'),
    path('confirm-delivery/DCS/', views.confirm_delivery, {'order_id': None}, name='confirm_delivery_masked'),

    path('get_delivery_status/<int:order_id>/', views.get_delivery_status, name='get_delivery_status'),
    path('get_delivery_status/DCS/', views.get_delivery_status, {'order_id': None}, name='get_delivery_status_masked'),

    path('get_server_ip/', views.get_server_ip, name='get_server_ip'),

    path('admin_disease_detection/', views.admin_disease_detection, name='admin_disease_detection'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    
# path('productslist/<int:product_id>/',views.productdetails, name='productdetails'),
    
#     path('wishlist', views.wishlist, name='wishlist'),
#     path('addwishlist/<int:product_id>/', views.addwishlist, name='addwishlist'),
#     path('removewishlist/<int:item_id>/', views.removewishlist, name='removewishlist'),
     
