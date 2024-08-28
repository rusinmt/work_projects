## Ad Hoc Archive Mirroring Project

In this notebook, I am documenting the task to synchronize the local archive with the IT department's centralized archive. The project identifies which files have been sent to the IT department for archiving and which ones are yet to be sent. This process involves several steps, including file processing, web scraping, and data comparison, effectively complementing the main storage by maintaining only what is missing from it.

The code utilizes the Scrapy tool to interact with an internal web interface. The scraper sends requests for each unique file identifier obtained from the local PDFs and extracts relevant information from the responses. This data is then saved as JSON Lines, yielding the links into<br> a dictionary, ensuring a full raw 
layer of preserved data for other applications.
The solution matches filenames processed to reflect the names of files in the on-premises directory. It then saves the findings as a CSV file, due to the large amount of data and long processing times, providing the code with a checkpoint to bounce off of, just in case. 

The whole idea of the project was to present the IT department with a clean update of documents. With the last cell, the code drops file paths that are already present in the central archive, leaving out those that are meant to be sent.
