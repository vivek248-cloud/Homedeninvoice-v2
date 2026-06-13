from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ==================================
        # STATIC FILES
        # ==================================
        if request.path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        # ==================================
        # MEDIA FILES
        # ==================================
        if (
            hasattr(settings, "MEDIA_URL")
            and request.path.startswith(settings.MEDIA_URL)
        ):
            return self.get_response(request)

        # ==================================
        # ADMIN
        # ==================================
        if request.path.startswith("/admin/"):
            return self.get_response(request)

        # ==================================
        # PUBLIC URLS
        # ==================================
        allowed_urls = [
            reverse("login"),
            reverse("logout"),
            reverse("client_login"),
            reverse("client_logout"),
        ]

        if request.path in allowed_urls:
            return self.get_response(request)

        # ==================================
        # PUBLIC INVOICE TOKEN LINKS
        # ==================================
        if request.path.startswith("/invoice/"):
            return self.get_response(request)

        # ==================================
        # CLIENT SESSION LOGIN
        # ==================================
        if request.session.get("client_id"):
            return self.get_response(request)

        # ==================================
        # DJANGO ADMIN LOGIN
        # ==================================
        if request.user.is_authenticated:

            timeout = getattr(
                settings,
                "SESSION_IDLE_TIMEOUT",
                3600
            )

            last_activity = request.session.get(
                "last_activity"
            )

            now_ts = timezone.now().timestamp()

            if last_activity:

                idle_time = now_ts - last_activity

                if (
                    idle_time > timeout
                    and request.method != "POST"
                ):
                    logout(request)
                    return redirect(
                        settings.LOGIN_URL
                    )

            request.session[
                "last_activity"
            ] = now_ts

            return self.get_response(request)

        # ==================================
        # NOT LOGGED IN
        # ==================================
        return redirect(settings.LOGIN_URL)