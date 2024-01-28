# SPDX-FileCopyrightText: 2023 Miguel P. Nunes adapted from OCRMyPDF-EasyOCR 2023 James R. Barlow
# SPDX-License-Identifier: MIT


"""Interface to AzureOCR."""

from __future__ import annotations

from typing import NamedTuple


class AzureOCRQuad(NamedTuple):
    ul: tuple[int, int]
    ur: tuple[int, int]
    lr: tuple[int, int]
    ll: tuple[int, int]


class AzureOCRResult(NamedTuple):
    """Result of OCR with AzureOCR."""

    quad: list
    text: str
    confidence: float


def tidy_azureocr_result(raw_result) -> AzureOCRResult:
    """Converts AzureOCR results to a more convenient format."""
    return AzureOCRResult(
        quad=[el for sublist in raw_result[0] for el in sublist],  # flatten list
        text=raw_result[1],
        confidence=raw_result[2],
    )

def extract_words(obj):
    # Read the JSON file
    data = serialize_to_json(obj)
    # Extract word details from the first page
    word_details = []
    if data["pages"] and len(data["pages"]) > 0:
        first_page = data["pages"][0]
        words = first_page.get("words", [])

        for word_info in words:
            polygon = word_info.get("polygon", [])
            #content = word_info.get("content", "").replace('\u20ab', ' ')
            content = word_info.get("content", "")
            confidence = word_info.get("confidence", 0)
            word_details.append((polygon, content, confidence))

    return word_details

# Serialize the result object
def serialize_to_json(obj):
    # Convert non-serializable fields
    if hasattr(obj, "__dict__"):
        obj_dict = {k: serialize_to_json(v) for k, v in obj.__dict__.items()}
        return obj_dict
    elif isinstance(obj, list):
        return [serialize_to_json(item) for item in obj]
    else:
        return obj
    