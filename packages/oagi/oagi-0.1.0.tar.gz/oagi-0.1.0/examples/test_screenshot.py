#!/usr/bin/env python3
"""
Example demonstrating the ScreenshotMaker functionality.
"""

import base64
from pathlib import Path

from oagi.screenshot_maker import ScreenshotMaker


def main():
    # Create a ScreenshotMaker instance
    maker = ScreenshotMaker()

    print("Taking a screenshot...")
    screenshot = maker()

    # Get the screenshot as bytes
    image_bytes = screenshot.read()
    print(f"Screenshot size: {len(image_bytes)} bytes")

    # You can also get the last screenshot
    last_screenshot = maker.last_image()
    assert last_screenshot is screenshot  # Should be the same object

    # Save the screenshot to a file for verification
    output_path = Path("test_screenshot.png")
    output_path.write_bytes(image_bytes)
    print(f"Screenshot saved to {output_path}")

    # Convert to base64 (as would be sent to API)
    b64_encoded = base64.b64encode(image_bytes).decode("utf-8")
    print(f"Base64 encoded size: {len(b64_encoded)} characters")
    print(f"First 100 characters of base64: {b64_encoded[:100]}...")

    print("\nScreenshot taken successfully!")


if __name__ == "__main__":
    main()
