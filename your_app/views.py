from django.shortcuts import get_object_or_404
from django.http import Http404

def your_view(request, id):
    # If the URL contains 'YK', return 404 since we don't want direct access
    if id == 'YK':
        raise Http404("Page not found")
        
    # Normal view logic using the numeric ID
    your_object = get_object_or_404(YourModel, id=id)
    
    return render(request, 'your_template.html', {
        'object': your_object,
    }) 