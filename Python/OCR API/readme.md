## Conecting to Adobe Pro API with Python

This project helps automate the process of performing OCR on scanned documents. After generating the Client ID and Client Secret using the Adobe UI, I used the Adobe PDF Services Python SDK to implement the desired functionality in the api() function. The process includes using OCR, splitting the PDF for desired first-page character recognition, and finally setting up a delay to extend the default 10 seconds.
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
In the next function, I am looking for an ID number and a title in the newly created text-based PDF of the first page of the original document. The logic is implemented to find capitalized text containing more than two words, excluding rows of text that could be a name and surname or numbers to filter out addresses. Additionally, I included logic to handle files with the same name by appending a suffix index to ensure uniqueness.
