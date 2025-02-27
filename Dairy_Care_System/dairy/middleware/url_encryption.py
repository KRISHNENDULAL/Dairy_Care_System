from django.http import Http404
from ..utils.encryption import URLEncryption

class URLDecryptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.url_encryption = URLEncryption()

    def __call__(self, request):
        # Decrypt URL parameters if they exist
        for key, value in request.GET.items():
            if key.endswith('_id'):
                decrypted_value = self.url_encryption.decrypt_id(value)
                if decrypted_value is not None:
                    request.GET = request.GET.copy()
                    request.GET[key] = decrypted_value

        # Handle POST data
        if request.method == 'POST':
            for key, value in request.POST.items():
                if key.endswith('_id'):
                    decrypted_value = self.url_encryption.decrypt_id(value)
                    if decrypted_value is not None:
                        request.POST = request.POST.copy()
                        request.POST[key] = decrypted_value

        return self.get_response(request) 