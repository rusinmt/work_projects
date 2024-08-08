import os
import PyPDF2
import re
import glob
from tqdm import tqdm
import logging

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.ocr_pdf_job import OCRPDFJob
from adobe.pdfservices.operation.pdfjobs.params.ocr_pdf.ocr_params import OCRParams
from adobe.pdfservices.operation.pdfjobs.params.ocr_pdf.ocr_supported_locale import OCRSupportedLocale
from adobe.pdfservices.operation.pdfjobs.params.ocr_pdf.ocr_supported_type import OCRSupportedType
from adobe.pdfservices.operation.pdfjobs.result.ocr_pdf_result import OCRPDFResult

from adobe.pdfservices.operation.config.client_config import ClientConfig

from adobe.pdfservices.operation.pdfjobs.jobs.split_pdf_job import SplitPDFJob
from adobe.pdfservices.operation.pdfjobs.params.split_pdf.split_pdf_params import SplitPDFParams
from adobe.pdfservices.operation.pdfjobs.result.split_pdf_result import SplitPDFResult

input_path = r"C:\Users\Mateusz\input"
ocr_path = r"C:\Users\Mateusz\ocr"
       
def api():
    try:
        pdf_files = glob.glob(os.path.join(input_path, '*.pdf'))
        for f in tqdm(pdf_files):
            with open(f, 'rb') as file:
                input_stream = file.read()
            file.close()
   
            # Initial setup, create credentials instance
            credentials = ServicePrincipalCredentials(
                client_id,
                client_secret
            )
   
            # Creates client config instance with custom time-outs.
            client_config: ClientConfig = ClientConfig(
                connect_timeout=3*60000,
                read_timeout=3*60000,
            )
   
            # Creates a PDF Services instance
            pdf_services = PDFServices(
                credentials=credentials,
                client_config=client_config
            )
   
            # Creates an asset(s) from source file(s) and upload
            input_asset = pdf_services.upload(input_stream=input_stream,
                                              mime_type=PDFServicesMediaType.PDF)
   
            ocr_pdf_params = OCRParams(
                ocr_locale=OCRSupportedLocale.PL_PL,
                ocr_type=OCRSupportedType.SEARCHABLE_IMAGE
            )
   
            # Implementing PDF page split
            split_pdf_params = SplitPDFParams(page_count=1)
            split_pdf_job = SplitPDFJob(input_asset, split_pdf_params)
            location = pdf_services.submit(split_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, SplitPDFResult)
            result_assets = pdf_services_response.get_result().get_assets()
   
            # Creates a new job instance
            ocr_pdf_job = OCRPDFJob(input_asset=result_assets[0], ocr_pdf_params=ocr_pdf_params)
   
            # Submit the job and gets the job result
            location = pdf_services.submit(ocr_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, OCRPDFResult)
   
            # Get content from the resulting asset(s)
            result_asset: CloudAsset = pdf_services_response.get_result().get_asset()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)
   
            # Creates an output stream and copy stream asset's content to it
            new_path = os.path.join(ocr_path, os.path.basename(f))
            with open(new_path, "wb") as file:
                file.write(stream_asset.get_input_stream())
   
    except (ServiceApiException, ServiceUsageException, SdkException) as e:
        logging.exception(f'Exception encountered while executing operation: {e}')
   

def find_capitalized_lines(text):
    lines = text.split('\n')
    capitalized_lines = [line for line in lines if line.isupper() and len(line.split()) > 2 and line.strip() and not re.search(r'\d', line)]
    return capitalized_lines

def rename():
    for filename in os.listdir(ocr_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(ocr_path, filename)
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                first_page = pdf_reader.pages[0].extract_text()  
                ref = re.search(r'\d{9}', first_page)
                ref = ref.group() if ref else ''  
                capitalized_lines = find_capitalized_lines(first_page)
                if capitalized_lines:
                    for line in capitalized_lines:
                        line = line.strip()
                        line = line[0].upper() + line[1:].lower()
                else:
                    print("No title")
                new_filename = f"{ref}_{line}.pdf"
                old_path = os.path.join(input_path, filename)
                new_path = os.path.join(input_path, new_filename)
                if filename in os.listdir(input_path):
                    i = 1
                    while os.path.exists(os.path.join(input_path, f"{ref}_{line}_{i}.pdf")):
                        i += 1
                    new_filename = f"{ref}_{line}_{i}.pdf"
                os.rename(old_path, new_path)
                file.close()
                os.remove(file_path)
def main():                  
    api()
    rename()
    print("Ready!")

if __name__ == "__main__":
    main()
