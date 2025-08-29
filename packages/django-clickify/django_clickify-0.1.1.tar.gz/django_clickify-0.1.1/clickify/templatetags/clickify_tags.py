from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def track_url(slug):
    """
    A template tag that returns the tracked URL for a TrackedLink slug.
    Usage: {% track_url 'my-link-slug' %}
    """

    return reverse('clickify:track_click', kwargs={'slug': slug})
