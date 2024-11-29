Scheduled ETL solution is a Scrapy-based application designed to scrape a webpage for court delivery information. It operates only on weekdays and excludes weekends and public holidays in Poland, ensuring that the scraper can be easily scheduled using a cron job on a server. The application checks the current date to confirm it is a weekday and not a holiday before proceeding with the scraping process.
<br>
It extracts necessary data related to court deliveries for the current day and uses the client's reference number to query a database, retrieving additional information required for the output. Client information is then used to fill a predefined template.
<br>
Finally, the completed output, in a form of an excel file, is uploaded to an SFTP server using the Paramiko library, ensuring secure file transfer.
