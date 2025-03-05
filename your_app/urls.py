from django.urls import path, re_path
from . import views

urlpatterns = [
    # ... existing code ...
    
    # Add these URL patterns for each view that uses IDs
    re_path(r'^path/to/view/(?P<id>\d+)/$', views.your_view, name='your_view'),
    re_path(r'^path/to/view/YK/$', views.your_view, name='your_view_masked'),
    
    # ... existing code ...
] 