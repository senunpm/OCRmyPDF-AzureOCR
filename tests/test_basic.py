# SPDX-FileCopyrightText: 2023 Miguel P. Nunes adapted from OCRMyPDF-EasyOCR 2023 James R. Barlow
# SPDX-License-Identifier: MIT

import ocrmypdf
import pikepdf
import pytest

import ocrmypdf_azureocr


def test_azureocr(resources, outpdf):
    
    ocrmypdf.ocr(resources / "jbig2.pdf", outpdf)
    #ocrmypdf.ocr(resources / "100page.pdf", outpdf)
    assert outpdf.exists()

    with pikepdf.open(outpdf) as pdf:
        assert "Azure" in str(pdf.docinfo["/Creator"])
    
    print(outpdf)