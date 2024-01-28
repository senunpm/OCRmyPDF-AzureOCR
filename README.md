# OCRmyPDF AzureOCR

This is a plugin to run OCRmyPDF with the AzureOCR engine, providing an alternative to the default Tesseract OCR engine used by OCRmyPDF. AzureOCR can offer improved accuracy and performance, especially for certain types of documents and languages.

This plugin is currently experimental and may not implement all features available in OCRmyPDF with Tesseract. It may still rely on Tesseract for certain operations.

This is an adaptation from the Plugin EasyOCR to OCRmyPDF.

## Installation
To use this plugin:

Ensure you have an Azure account and access to the Azure Cognitive Services resource. You will need to obtain an endpoint URL and an API key from Azure.

Clone the repository:
```bash
    git clone https://github.com/senunpm/OCRmyPDF-AzureOCR.git
```

Install the plugin to the same virtual environment or conda environment as OCRmyPDF:
```bash
pip install ./OCRmyPDF-AzureOCR
```

Rename the env_example file to .env and update it with your Azure Cognitive Services endpoint and API key:
```bash
cp  .env_example .env
```
Modify ENDPOINT and API_KEY to match your own

## Troubleshooting


## To do
Contributions, especially pull requests are quite welcome!

At the moment this plugin is alpha status and missing some essential features:
- Tesseract is still required for some functions