from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter — redirects to JWT bridge after login."""

    def get_login_redirect_url(self, request):
        return '/auth/oauth-success/'


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter — sends OAuth users to JWT bridge."""

    def get_connect_redirect_url(self, request, socialaccount):
        return '/auth/oauth-success/'

    def pre_social_login(self, request, sociallogin):
        """
        Auto-connect Google account to existing user if email matches.
        Prevents duplicate accounts.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if sociallogin.is_existing:
            return

        if not sociallogin.email_addresses:
            return

        email = sociallogin.email_addresses[0].email.lower()
        try:
            user = User.objects.get(email__iexact=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            pass
