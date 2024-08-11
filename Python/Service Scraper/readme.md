## Service History Scraper

This ETL script automates data extraction and document retrieval from the e-court system, using Selenium. It begins by logging into the system and navigating to the user's deliveries page, where it sets a specified date range filter, in this case the last seven days. The script then extracts data for multiple options, downloading XLS files in the process. These files are transformed using pandas, combining data from multiple sources into a single DataFrame, including the extraction of reference numbers. The processed data is then saved as a CSV file with the current date in the filename, serving as a raw tier of data. Following this, the script uses the extracted data to navigate the website and download associated PDF documents, renaming and organizing them based on reference numbers and case details.
```python
options.add_experimental_option("prefs", {
    "plugins.always_open_pdf_externally": True,
    "download.default_directory": pdf_path
})
```
Enabling experimental options in Chrome allowed for retrieving PDF documents without the necessity of accessing multiple levels of shadow DOM in the web page code.

This automated ETL process significantly streamlines extracting court delivery data and retrieving associated documents in a single execution. The end product is a PDF files archive that will be added to the company's internal application storage and will be accessed by users. The code skips downloading files with the same title to avoid producing duplicated data in the dedicated storage. The  The data engineering work in this script highlights a comprehensive skill set in web automation, data extraction, and ETL pipeline design. It also exhibits expertise in handling various file formats, including XLS, CSV, PDF, and HTML, showcasing the ability to work with both structured and unstructured data. The entire process is structured as an efficient ETL pipeline, indicating a solid understanding of data workflow design principles.
