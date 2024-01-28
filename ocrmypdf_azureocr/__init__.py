# SPDX-FileCopyrightText: 2023 Miguel P. Nunes adapted from OCRMyPDF-EasyOCR 2023 James R. Barlow
# SPDX-License-Identifier: MIT


"""AzureOCR plugin for OCRmyPDF."""

from __future__ import annotations

import logging
import os
from multiprocessing import Semaphore

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

import time

import cv2 as cv
import pluggy
from ocrmypdf import OcrEngine, hookimpl
from ocrmypdf._exec import tesseract

from ocrmypdf_azureocr._cv import detect_skew
from ocrmypdf_azureocr._azureocr import tidy_azureocr_result, extract_words
from ocrmypdf_azureocr._pdf import azureocr_to_pikepdf

from dotenv import load_dotenv

log = logging.getLogger(__name__)

GPU_SEMAPHORE = Semaphore(3)

# Load the environment variables from .env file
load_dotenv()

endpoint = os.getenv('ENDPOINT')
api_key = os.getenv('API_KEY')


# Initialize Document Analysis Client
document_analysis_client = DocumentAnalysisClient(endpoint=endpoint,credential=AzureKeyCredential(api_key))

    
ISO_639_3_2: dict[str, str] = {
    "afr": "af",
    "alb": "sq",
    "ara": "ar",
    "aze": "az",
    "bel": "be",
    "ben": "bn",
    "bos": "bs",
    "bul": "bg",
    "cat": "ca",
    "ces": "cs",
    "che": "che",
    "chi_sim": "ch_sim",
    "chi_tra": "ch_tra",
    "cym": "cy",
    "cze": "cs",
    "dan": "da",
    "deu": "de",
    "dut": "nl",
    "eng": "en",
    "est": "et",
    "esp": "es",
    "fra": "fr",
    "gle": "ga",
    "hin": "hi",
    "hrv": "hr",
    "hun": "hu",
    "ice": "is",
    "ind": "id",
    "isl": "is",
    "ita": "it",
    "jpn": "ja",
    "kor": "ko",
    "kur": "ku",
    "lat": "la",
    "lav": "lv",
    "lit": "lt",
    "may": "ms",
    "mlt": "mt",
    "mon": "mn",
    "msa": "ms",
    "nep": "ne",
    "nld": "nl",
    "nor": "no",
    "oci": "oc",
    "per": "fa",
    "pol": "pl",
    "por": "pt",
    "rum": "ro",
    "ron": "ro",
    "rus": "ru",
    "slo": "sk",
    "slk": "sk",
    "slv": "sl",
    "spa": "es",
    "swa": "sw",
    "swe": "sv",
    "tam": "ta",
    "tha": "th",
    "tgl": "tl",
    "tur": "tr",
    "ukr": "uk",
    "urd": "ur",
    "vie": "vi",
}


@hookimpl
def initialize(plugin_manager: pluggy.PluginManager):
    pass


@hookimpl
def add_options(parser):
    azureocr_options = parser.add_argument_group(
        "AzureOCR", "Advanced control of AzureOCR"
    )
    azureocr_options.add_argument("--azureocr", action="store_false", dest="cpu")

@staticmethod
def call_azure_service(input_file, attempts=5, initial_delay=1):
    """
    Calls the Azure service with exponential backoff.
    """
    for attempt in range(attempts):
        try:
            with open(input_file, "rb") as f:
                poller = document_analysis_client.begin_analyze_document(
                    "prebuilt-read", document=f)
                reader = poller.result()
            return reader
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(initial_delay * (2 ** attempt))  # Exponential backoff

    print("All attempts to call the Azure service have failed.")
    return None

class AzureOCREngine(OcrEngine):
    """Implements OCR with AzureOCR."""

    @staticmethod
    def version():
        return "0.0.1"

    @staticmethod
    def creator_tag(options):
        tag = "-PDF" if options.pdf_renderer == "sandwich" else ""
        return f"AzureOCR{tag} {AzureOCREngine.version()}"

    def __str__(self):
        return f"AzureOCR {AzureOCREngine.version()}"

    @staticmethod
    def languages(options):
        return ISO_639_3_2.keys()

    @staticmethod
    def get_orientation(input_file, options):
        return tesseract.get_orientation(
            input_file,
            engine_mode=options.tesseract_oem,
            timeout=options.tesseract_non_ocr_timeout,
        )

    @staticmethod
    def get_deskew(input_file, options) -> float:
        img = cv.imread(os.fspath(input_file))
        angle = detect_skew(img)
        log.debug(f"Detected skew angle: {angle:.2f} degrees")
        return angle

    @staticmethod
    def generate_hocr(input_file, output_hocr, output_text, options):
        raise NotImplementedError("Plugin AzureOCR hOCR not implemented")

    @staticmethod
    def generate_pdf(input_file, output_pdf, output_text, options):
        languages = [ISO_639_3_2[lang] for lang in options.languages]
        
        #Locale not implemented - Documentation  https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/language-support-ocr?view=doc-intel-4.0.0&tabs=read-hand%2Clayout-hand%2Cgeneral Model ID: prebuilt-read
        #l=str(languages[0])
        #Language code optional
        #Document Intelligence's deep learning based universal models extract all multi-lingual text in your documents, including text lines with mixed languages, and don't require specifying a language code.
        #Don't provide the language code as the parameter unless you are sure about the language and want to force the service to apply only the relevant model. Otherwise, the service may return incomplete and incorrect text.
        #Also, It's not necessary to specify a locale. This is an optional parameter. The Document Intelligence deep-learning technology will auto-detect the text language in your image.
        
        #initialize raw_results
        raw_results =[]
        
        # Read the file
        with GPU_SEMAPHORE:
            reader = call_azure_service(input_file)
            if reader is not None:
                raw_results = extract_words(reader)
            else:
                # Handle the failure case
                pass
                        
        results = [tidy_azureocr_result(r) for r in raw_results]

        text = " ".join([result.text for result in results])
        output_text.write_text(text,encoding='utf-8')

        # azureocr_to_pdf(input_file, 1.0, results, output_pdf)
        azureocr_to_pikepdf(input_file, 1.0, results, output_pdf)


@hookimpl
def get_ocr_engine():
    return AzureOCREngine()
