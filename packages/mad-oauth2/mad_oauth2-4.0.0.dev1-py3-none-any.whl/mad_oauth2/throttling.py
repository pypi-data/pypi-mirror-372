from mad_oauth2.models import Throttle
from mad_oauth2.settings import oauth2_settings
from rest_framework.throttling import SimpleRateThrottle


class ThrottleClass:
    def __init__(self):
        self.rate = dict(Throttle.objects.values_list("scope", "rate"))

    def getThrottlingRates(self):
        return self.rate


def getThrottling():
    throttling = oauth2_settings.THROTTLE_CLASS()
    return throttling.getThrottlingRates()


class BaseScopedRateThrottle(SimpleRateThrottle):
    THROTTLE_RATES = getThrottling()
    scope_attr = "throttle_scope"

    def __init__(self):
        pass

    def allow_request(self, request, view):
        # We can only determine the scope once we're called by the view.
        self.scope = getattr(view, self.scope_attr, None)

        # If a view does not have a `throttle_scope` always allow the request
        if not self.scope:
            return True

        # Determine the allowed request rate as we normally would during
        # the `__init__` call.
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)

        # We can now proceed as normal.
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        """
        If `view.throttle_scope` is not set, don't apply this throttle.
        Otherwise generate the unique cache key by concatenating the user id
        with the '.throttle_scope` property of the view.
        """
        if request.user is not None and request.user.is_authenticated:
            ident = request.user.pk
        else:
            # app_data = getApplicationDataFromRequest(request)
            # ident = app_data['application'].id
            ident = self.get_ident(request)

        return self.cache_format % {"scope": self.scope, "ident": ident}
