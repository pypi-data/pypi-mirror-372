from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import TrackedLink
from .views import track_click
from .utils import create_click_log


@method_decorator(
    ratelimit(
        key='ip',
        rate=lambda r, g: getattr(settings, 'CLICKIFY_RATE_LIMIT', '5/m'),
        block=True
    ),
    name='post'
)
class TrackClickAPIView(APIView):
    """ An API View to track a click for a TrackedLink. """

    def post(self, request, slug, format=None):
        """ Tracks a click for the given slug. """
        target = get_object_or_404(TrackedLink, slug=slug)

        # Use the helper function with the underlying Django request
        create_click_log(target=target, request=request._request)

        return Response(
            {"message": "Click tracked successfully",
                "target_url": target.target_url},
            status=status.HTTP_200_OK
        )

    def throttled(self, request, wait):
        """ 
        Custom handler for when a request is rate-limited 
        Note: This is for DRF's own throttling, not django-ratelimit.
        """

        return Response(
            {"error": "Rate limit exceeded. Please try again later"},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
