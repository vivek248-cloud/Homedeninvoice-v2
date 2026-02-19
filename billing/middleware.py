from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import logout


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ✅ Allow static files
        if request.path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        # ✅ Allow media files
        if hasattr(settings, "MEDIA_URL") and request.path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # ✅ Allowed URLs
        allowed_urls = [
            reverse('login'),
            reverse('logout'),
        ]

        # ✅ Allow admin completely
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        if request.path in allowed_urls:
            return self.get_response(request)

        # 🔐 If authenticated → check inactivity
        if request.user.is_authenticated:

            timeout = getattr(settings, "SESSION_IDLE_TIMEOUT", 900)
            last_activity = request.session.get('last_activity')

            now_ts = timezone.now().timestamp()

            if last_activity:
                idle_time = now_ts - last_activity

                if idle_time > timeout:
                    logout(request)
                    return redirect(settings.LOGIN_URL)

            # ✅ update last activity
            request.session['last_activity'] = now_ts

        # 🚫 If not authenticated
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)
