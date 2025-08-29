# Django Clickify

[![PyPI version](https://badge.fury.io/py/django-clickify.svg)](https://badge.fury.io/py/django-clickify)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple Django app to track clicks on any link (e.g., affiliate links, outbound links, file downloads) with rate limiting, IP filtering, and geolocation.

## Features

*   **Click Tracking**: Logs every click on a tracked link, including IP address, user agent, and timestamp.
*   **Geolocation**: Automatically enriches click logs with the country and city of the request's IP address via a web API.
*   **Rate Limiting**: Prevents abuse by limiting the number of clicks per IP address in a given timeframe.
*   **IP Filtering**: Easily configure allowlists and blocklists for IP addresses.
*   **Secure**: Protects against path traversal attacks.
*   **Django Admin Integration**: Create and manage your tracked links directly in the Django admin.
*   **Template Tag & DRF View**: Provides both a simple template tag for traditional Django templates and a DRF API view for headless/JavaScript applications.

## Installation

1.  Install the package from PyPI:

    ```bash
    pip install django-clickify
    ```

2.  Add `'clickify'` to your `INSTALLED_APPS` in `settings.py`:

    ```python
    INSTALLED_APPS = [
        # ...
        'clickify',
    ]
    ```

3.  Run migrations to create the necessary database models:

    ```bash
    python manage.py migrate
    ```

4.  **For API support (Optional)**: If you plan to use the DRF view, you must also install `djangorestframework` and add it to your `INSTALLED_APPS`.

    ```bash
    pip install django-clickify[drf]
    ```
    ```python
    INSTALLED_APPS = [
        # ...
        'rest_framework',
        'clickify',
    ]
    ```

## Configuration

### 1. Middleware (for IP Filtering)

To enable the IP allowlist and blocklist feature, add the `IPFilterMiddleware` to your `settings.py`.

```python
MIDDLEWARE = [
    # ...
    'clickify.middleware.IPFilterMiddleware',
    # ...
]
```

### 2. Settings (Optional)

You can customize the behavior of `django-clickify` by adding the following settings to your `settings.py`:

*   `CLICKIFY_GEOLOCATION`: A boolean to enable or disable geolocation. Defaults to `True`.
*   `CLICKIFY_RATE_LIMIT`: The rate limit for clicks. Defaults to `'5/m'`.
*   `CLICKIFY_IP_ALLOWLIST`: A list of IP addresses that are always allowed. Defaults to `[]`.
*   `CLICKIFY_IP_BLOCKLIST`: A list of IP addresses that are always blocked. Defaults to `[]`.

## Testing

To run the tests for this project, you'll need to have `pytest` and `pytest-django` installed. You can install them with:

```bash
pip install pytest pytest-django
```

Then, you can run the tests from the root of the project with:

```bash
poetry run pytest
```

This will run all the tests in the `tests/` directory.

## Usage

### Option 1: Template-Based Usage

This is the standard way to use the app in traditional Django projects.

#### Step 1: Create a Tracked Link

In your Django Admin, go to the "Clickify" section and create a new "Tracked Link". This target can be any URL you want to track clicks on.

The `Target Url` can point to any type of file (e.g., PDF, ZIP, MP3, MP4, TXT) or any webpage. The link can be hosted anywhere, such as Amazon S3, a personal blog, or an affiliate partner's site.

*   **Name:** `Monthly Report PDF`
*   **Slug:** `monthly-report-pdf` (this will be auto-populated from the name)
*   **Target Url:** `https://your-s3-bucket.s3.amazonaws.com/reports/monthly-summary.pdf`

#### Step 2: Include Clickify URLs

In your project's `urls.py`, include the `clickify` URL patterns.

```python
# your_project/urls.py
from django.urls import path, include

urlpatterns = [
    # ... your other urls
    path('track/', include('clickify.urls', namespace='clickify')),
]
```

#### Step 3: Create the Tracked Link

In your Django template, use the `track_url` template tag to generate the tracking link. Use the slug of the `TrackedLink` you created in Step 1.

```html
<!-- your_app/templates/my_template.html -->
{% load clickify_tags %}

<a href="{% track_url 'monthly-report-pdf' %}">
  Get Monthly Summary
</a>
```

### Option 2: API Usage (for Headless/JS Frameworks)

If you are using a JavaScript frontend (like React, Vue, etc.) or need a programmatic way to get a tracked URL, you can use the DRF API endpoint.

#### Step 1: Create a Tracked Link

Follow Step 1 from the template-based usage above.

#### Step 2: Include Clickify DRF URLs

In your project's `urls.py`, include the `clickify.drf_urls` patterns.

```python
# your_project/urls.py
from django.urls import path, include

urlpatterns = [
    # ... your other urls
    path('api/track/', include('clickify.drf_urls', namespace='clickify-api')),
]
```

#### Step 3: Make the API Request

From your frontend, make a `POST` request to the API endpoint using the slug of your `TrackedLink`.

**Endpoint**: `POST /api/track/<slug>/`

A successful request will track the click and return the actual file URL, which you can then use to trigger the click or redirection on the client-side.

**Example using JavaScript `fetch`:**

```javascript
fetch('/api/track/monthly-report-pdf/', {
    method: 'POST',
    headers: {
        // Include CSRF token if necessary for your setup
        'X-CSRFToken': 'YourCsrfTokenHere' 
    }
})
.then(response => response.json())
.then(data => {
    if (data.target_url) {
        console.log("Click tracked. Redirecting to:", data.target_url);
        // Redirect the user to the URL
        window.location.href = data.target_url;
    } else {
        console.error("Failed to track click:", data);
    }
})
.catch(error => {
    console.error('Error:', error);
});
```

**Successful Response (`200 OK`):**
```json
{
    "message": "Click tracked successfully",
    "target_url": "https://your-s3-bucket.s3.amazonaws.com/reports/monthly-summary.pdf"
}
```

**Failure Responses**

If the request fails, you might receive one of the following error responses:

*   **404 Not Found:**

    ```json
    {
        "detail": "Not found."
    }
    ```

*   **429 Too Many Requests:**

    ```json
    {
        "error": "Rate limit exceeded. Please try again later"
    }
    ```

*   **403 Forbidden:** (If IP filtering is enabled and the IP is blocked)

    This will typically return a plain text response like:
    ```
    IP address blocked.
    ```

### How It Works

1.  A user clicks a tracked link (`/track/monthly-report-pdf/`) or a `POST` request is sent to the API.
2.  The view or API view records the click event in the database, associating it with the correct `TrackedLink`.
3.  The standard view issues a `302 Redirect` to the `target_url`. The API view returns a JSON response containing the `target_url`.
4.  The user's browser is redirected to the final destination.

This approach is powerful because if you ever need to change the link's destination, you only need to update the `Target Url` in the Django Admin. All your tracked links and API calls will continue to work correctly.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and add tests for them.
4.  Ensure the tests pass by running `poetry run pytest`.
5.  Create a pull request with a clear description of your changes.