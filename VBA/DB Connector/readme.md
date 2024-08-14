## Automate Database Updates with Excel VBA

I have developed a VBA solution that offers a seamless way to connect to a PostgreSQL database and retrieve data with minimal effort.<br> A universal tool for managment without the use of any tool for querying. This provides up to date reads and combined with potential of ad hoc analysis and visuals of Excel workbook.

Firstly to confirm acess, the process requires user to login. Within created UserForm window.
<p align="center">
    <img src="https://github.com/user-attachments/assets/73ed9200-daa0-411d-80ed-3e99dbf48a1e" style="width: 35%;">
</p>
By selecting an Excel file containing an SQL query, from a pop up window, users can instantly access the database and import the results into the template workbook.
```sql
Set dialog = Application.FileDialog(msoFileDialogFilePicker)
    dialog.Title = "Select an Excel File"
    dialog.Filters.Clear
    dialog.Filters.Add "Excel Files", "*.xls; *.xlsx; *.xlsm"
```
Analytics team can share multpiple multiple reports in a form of Excel file exported via DataGrip with automaticly automatically created 'script' worksheet.
VBA code is assigned to a button from Controls in the Developer tab.
<p align="center">
    <img src="https://github.com/user-attachments/assets/b77adab6-a219-4bd3-bad2-5230f550c89e" style="width: 35%;">
</p>

I have enabled the Microsoft ActiveX Data Objects with the MSDASQL provider, which acts as a bridge between OLE DB and ODBC.
<p align="center">
    <img src="https://github.com/user-attachments/assets/255d0912-4f0e-4c4e-b474-4338a56fc60d" style="width: 50%;">
</p>
The query results with headers are inserted just below the trigger button, after cleaning the worksheet cells to ensure up-to-date values on read. The code enables users to refresh the connected script with an additional Refresh button that uses the extracted query, stored in an unused cell of the workbook, in a similar fashion to the DBConnect procedure.
