## Conecting to Adobe Pro API with Python

This project helps to automate performing OCR on scanned documents. After generating Client ID and Client Secret with Adobe UI, I have used Adobe PDF Services Python SDK to implement desired mechanics into api() function. Using OCR, spliting the PDF, for desired first page character recodnition, and finally setting up a delay to extebnd default 10 second.

```python
 client_config: ClientConfig = ClientConfig(
                connect_timeout=3*60000,
                read_timeout=3*60000,
            )

            pdf_services = PDFServices(
                credentials=credentials,
                client_config=client_config
            )
```            
