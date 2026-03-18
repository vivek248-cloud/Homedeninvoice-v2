from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import logout


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Allow static files
        if request.path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        # Allow media files
        if hasattr(settings, "MEDIA_URL") and request.path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # Allow admin
        if request.path.startswith("/admin/"):
            return self.get_response(request)

        # Allowed public URLs
        allowed_urls = [
            reverse("login"),
            reverse("logout"),
            reverse("client_login"),
            reverse("client_logout"),
        ]

        if request.path in allowed_urls:
            return self.get_response(request)

        # allow client invoice links with token
        
        if request.path.startswith("/client/invoice/"):
            return self.get_response(request)

        # ✅ FIX: allow public invoice
        # allow public invoice by name
        if request.resolver_match and request.resolver_match.url_name == "public_invoice":
            return self.get_response(request)

        # allow client dashboard
        if request.path.startswith("/client/dashboard"):
            return self.get_response(request)

        # If user not logged in
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        # Idle timeout check
        timeout = getattr(settings, "SESSION_IDLE_TIMEOUT", 3600)
        last_activity = request.session.get("last_activity")

        now_ts = timezone.now().timestamp()

        if last_activity:
            idle_time = now_ts - last_activity

            # 🔑 IMPORTANT: allow POST request (form submission)
            if idle_time > timeout and request.method != "POST":
                logout(request)
                return redirect(settings.LOGIN_URL)

        # Update activity timestamp
        request.session["last_activity"] = now_ts

        return self.get_response(request)