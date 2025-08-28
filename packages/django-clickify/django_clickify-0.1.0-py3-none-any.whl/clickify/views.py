from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.conf import settings
from django_ratelimit.exceptions import Ratelimited
from django_ratelimit.decorators import ratelimit
from .models import TrackedLink
from .utils import create_click_log


@ratelimit(key='ip', rate=lambda r, g: getattr(settings, 'CLICKIFY_RATE_LIMIT', '5/m'), block=True)
def track_click(request, slug):
    """
    Tracks a click for a TrackedLink and then redirects to its actual URL.
    """

    try:
        target = get_object_or_404(TrackedLink, slug=slug)
        # Call the helper function to do the actual tracking
        create_click_log(target=target, request=request)
        return HttpResponseRedirect(target.target_url)
    except Ratelimited:
        return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
