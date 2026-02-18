from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Allow static files
        if request.path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        # Allow media files (if any)
        if hasattr(settings, "MEDIA_URL") and request.path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # Allow login, logout, admin
        allowed_urls = [
            reverse('login'),
            reverse('logout'),
            '/admin/',
        ]

        if request.path.startswith('/admin/'):
            return self.get_response(request)

        if request.path in allowed_urls:
            return self.get_response(request)

        # If user not authenticated → redirect
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)
