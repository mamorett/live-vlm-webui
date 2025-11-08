"""End-to-end tests using a real browser (Playwright).

These tests catch issues that HTTP-level tests cannot:
- Missing images causing browser errors
- Broken CSS/JS loading
- Frontend JavaScript errors
- Visual regressions
- Browser console errors

Install: pip install playwright pytest-playwright
Setup: playwright install chromium
"""

import pytest
import re


@pytest.mark.e2e
@pytest.mark.slow
def test_page_loads_without_errors(page):
    """Test that main page loads without console errors or missing assets."""
    # Track console messages
    console_msgs = []
    page.on("console", lambda msg: console_msgs.append(msg))

    # Track failed requests (404s, etc.)
    failed_requests = []
    page.on("requestfailed", lambda request: failed_requests.append(request))

    # Navigate to page
    page.goto("http://localhost:8090")

    # Wait for page to load
    page.wait_for_load_state("networkidle")

    # Check for failed requests (missing images, CSS, JS)
    if failed_requests:
        failed_urls = [req.url for req in failed_requests]
        pytest.fail(
            f"Failed to load {len(failed_requests)} resources:\n" +
            "\n".join(failed_urls)
        )

    # Check for console errors (ignore expected webcam errors in test environment)
    errors = [msg for msg in console_msgs if msg.type == "error"]
    # Filter out expected errors
    unexpected_errors = [
        msg for msg in errors
        if "Requested device not found" not in msg.text  # No webcam in headless browser
        and "NotFoundError" not in msg.text  # Camera not found is expected
    ]
    if unexpected_errors:
        error_texts = [msg.text for msg in unexpected_errors]
        pytest.fail(
            f"Page has {len(unexpected_errors)} unexpected console errors:\n" +
            "\n".join(error_texts)
        )


@pytest.mark.e2e
@pytest.mark.slow
def test_no_missing_images(page):
    """Test that all images load successfully (catches missing /images/ dir)."""
    page.goto("http://localhost:8090")
    page.wait_for_load_state("networkidle")

    # Get all images
    images = page.query_selector_all("img")

    missing_images = []
    for img in images:
        # Check if image loaded successfully
        natural_width = img.evaluate("el => el.naturalWidth")
        src = img.get_attribute("src")

        if natural_width == 0:
            missing_images.append(src)

    assert len(missing_images) == 0, \
        f"Failed to load {len(missing_images)} images: {missing_images}"


@pytest.mark.e2e
@pytest.mark.slow
def test_no_404_in_network_requests(page):
    """Test that no requests return 404 (catches missing static files)."""
    responses_404 = []

    def handle_response(response):
        if response.status == 404:
            responses_404.append(response.url)

    page.on("response", handle_response)

    # Navigate and wait for all resources
    page.goto("http://localhost:8090")
    page.wait_for_load_state("networkidle")

    assert len(responses_404) == 0, \
        f"Found {len(responses_404)} 404 responses:\n" + "\n".join(responses_404)


@pytest.mark.e2e
@pytest.mark.slow
def test_no_flashing_screen(page):
    """Test that screen doesn't flash from repeated failed image loads."""
    page.goto("http://localhost:8090")

    # Track image request counts
    image_requests = {}

    def track_request(request):
        url = request.url
        if any(url.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
            image_requests[url] = image_requests.get(url, 0) + 1

    page.on("request", track_request)

    # Wait and observe
    page.wait_for_timeout(3000)  # Wait 3 seconds

    # Check if any image was requested multiple times (sign of reload loop)
    repeated_requests = {
        url: count for url, count in image_requests.items() if count > 2
    }

    assert len(repeated_requests) == 0, \
        f"Images being repeatedly requested (flashing):\n" + \
        "\n".join(f"{url}: {count} requests" for url, count in repeated_requests.items())


@pytest.mark.e2e
def test_all_static_assets_load(page):
    """Test that all CSS, JS, and image assets load successfully."""
    failed_resources = []

    def check_response(response):
        if response.status >= 400:
            # Check if it's a static asset
            url = response.url
            if any(ext in url for ext in ['.css', '.js', '.png', '.jpg', '.svg', '.ico']):
                failed_resources.append(f"{url} ({response.status})")

    page.on("response", check_response)

    page.goto("http://localhost:8090")
    page.wait_for_load_state("networkidle")

    assert len(failed_resources) == 0, \
        f"Failed to load static assets:\n" + "\n".join(failed_resources)


@pytest.mark.e2e
@pytest.mark.slow
def test_webcam_interface_visible(page):
    """Test that the webcam interface loads properly."""
    page.goto("http://localhost:8090")
    page.wait_for_load_state("networkidle")

    # Check that key UI elements are visible
    # Adjust selectors based on your actual UI
    assert page.is_visible("video"), "Video element not found"

    # Check that no error messages are shown
    error_selectors = [".error", ".alert-danger", "[role='alert']"]
    for selector in error_selectors:
        elements = page.query_selector_all(selector)
        visible_errors = [el for el in elements if el.is_visible()]
        assert len(visible_errors) == 0, \
            f"Found {len(visible_errors)} error messages on page"


@pytest.mark.e2e
def test_docker_container_has_images(page):
    """
    Test specifically for the Docker issue: /images/ directory missing.

    This test would have caught the issue where the images/ directory
    wasn't copied into the Docker container.

    TODO: Add favicon.ico and logo.png for better web app UX
    """
    # Use fetch API instead of navigation to check images without triggering downloads
    page.goto("http://localhost:8090")

    # Test actual image paths that exist in your project
    # These are the hardware images currently in /images/
    common_images = [
        "/images/jetson-agx-orin-devkit_256px.png",
        "/images/jetson-agx-thor-devkit_256px.png",
        "/images/dgx-spark_256px.png",
    ]

    for image_path in common_images:
        # Use fetch API to check without navigating/downloading
        response_status = page.evaluate(f"""
            fetch('{image_path}')
                .then(r => r.status)
                .catch(() => 0)
        """)
        assert response_status == 200, \
            f"Image missing from container: {image_path} " \
            f"(Did you forget to COPY images/ in Dockerfile?)"


# Configuration for Playwright
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "record_video_dir": "test-results/videos/",  # Record video of tests
    }


@pytest.fixture(scope="function")
def context(context):
    """Configure context to capture console logs and failed requests."""
    # Videos are already recorded via browser_context_args
    yield context

