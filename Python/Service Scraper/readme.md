## Service History Scraper

This ETL script automates data extraction and document retrieval from the e-court system, using Selenium. It begins by logging into the system and navigating to the user's deliveries page, where it sets a specified date range filter, in this case the last seven days. The script then extracts data, downloading XLS files in the process. Data is transformed using Pandas, combining data from multiple sources into a single DataFrame, including the extraction of reference numbers. The processed data is then saved as a CSV file with the current date in the filename, serving as a raw tier of data. Following this, the script uses the extracted data to navigate the website and download associated PDF documents, renaming and organizing them based on reference numbers and case details.
```python
options.add_experimental_option("prefs", {
    "plugins.always_open_pdf_externally": True,
    "download.default_directory": pdf_path
})
```
Enabling experimental options in Chrome allowed for retrieving PDF documents without the necessity of accessing multiple levels of shadow DOM in the web page code.

This automated ETL process significantly streamlines extracting court delivery data and retrieving associated documents in a single execution.Output will transform collected names for the files and automatically upload them to internal archive to be accessed by users. The code skips downloading a file that is already in a specified history (hist.txt), that is a list of files procesed.
```python
if any(file_name in f for f in hist):
                continue
            elif file_name in os.listdir(pdf_path) and not any(file_name in f for f in hist):
                with open(lista, 'a', encoding='utf-8') as f:
                    f.write(file_name + '\n')
                continue      
            elif input_button and 'name' in input_button.attrs:
                button_name = input_button['name']
                button_xpath = f"//input[@name='{button_name}']"
                time.sleep(2)
                click(driver, (By.XPATH, button_xpath))
                time.sleep(2)
                files = [f for f in os.listdir(pdf_path) if f.endswith('.pdf') and f.startswith('plik')]           
                if files:
                    og = os.path.join(pdf_path, files[0])
                    file_path = os.path.join(pdf_path, file_name)
                    i = 0
                    while True:
                        try:
                            os.rename(og, file_path)
                            with open(lista, 'a', encoding='utf-8') as f:
                                f.write(file_name + '\n')
                            break
                        except FileExistsError:
                            i += 1
                            file_name = f"{ref} - {sygnatura}_{i} - {opis}.pdf"
```
The data engineering work in this script highlights a comprehensive skill set in web automation, data extraction, and ETL pipeline design.<br> It also exhibits expertise in handling various file formats, including XLS, CSV, PDF, and HTML, showcasing the ability to work with both structured and unstructured data. The entire process is structured as an efficient ETL pipeline, indicating a solid understanding of data workflow design principles.
