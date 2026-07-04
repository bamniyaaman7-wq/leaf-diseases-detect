"""Utility helpers for the LeafCare AI project."""

import base64
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def summarize_result(result: Optional[Dict[str, Any]]) -> str:
    """Return a short human-friendly summary for a detection result."""
    if not isinstance(result, dict):
        return "The analysis could not be completed right now. Please try again in a moment."

    if result.get("disease_type") == "invalid_image":
        return "The image does not look like a clear leaf photo. Please upload a close-up leaf image with good lighting."

    if result.get("disease_detected"):
        disease_name = result.get("disease_name") or "a plant health issue"
        severity = result.get("severity") or "unknown"
        confidence = result.get("confidence") or "unknown"
        return f"{disease_name} is likely present. Severity: {severity}; confidence: {confidence}%."

    return "No disease signs were detected. The leaf appears healthy, but image quality can affect the result."


def _load_detector():
    """Import the detector lazily so the utilities remain lightweight."""
    sys.path.insert(0, str(Path(__file__).parent / "Leaf Disease"))
    from main import LeafDiseaseDetector

    return LeafDiseaseDetector()


def test_with_base64_data(base64_image_string: str):
    """Run disease detection with base64 image data."""
    try:
        detector = _load_detector()
        result = detector.analyze_leaf_image_base64(base64_image_string)
        print(json.dumps(result, indent=2))
        return result
    except Exception as exc:
        print(f'{{"error": "{str(exc)}"}}')
        return None


def convert_image_to_base64_and_test(image_bytes: bytes):
    """Convert image bytes to base64 and analyze them."""
    try:
        if not image_bytes:
            print('{"error": "No image bytes provided"}')
            return None

        if isinstance(image_bytes, (str, Path)):
            image_bytes = Path(image_bytes).read_bytes()

        base64_string = base64.b64encode(image_bytes).decode("utf-8")
        print(f"Converted image to base64 ({len(base64_string)} characters)")
        return test_with_base64_data(base64_string)
    except Exception as exc:
        print(f'{{"error": "{str(exc)}"}}')
        return None


def main():
    """Run a small smoke test with the sample image."""
    image_path = "Media/brown-spot-4 (1).jpg"
    convert_image_to_base64_and_test(image_path)


if __name__ == "__main__":
    main()
