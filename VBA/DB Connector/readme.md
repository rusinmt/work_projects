## Automate Database Updates with Excel VBA

I have developed an a VBA solution offering a seamless way to connect to PostgreSQL database and retrieve data with minimal effort. A universal tool for managment management without the nesesity necessity of setting up a credential connection without a tool for querying. This provides up to date reads and combines the benefits of quick ad hoc analysis and visuals of Excel workbook.

By selecting an Excel file containing an SQL query, from a pop up window, users can instantly access the database and import the results into the template workbook.
'''sql
Set dialog = Application.FileDialog(msoFileDialogFilePicker)
    dialog.Title = "Select an Excel File"
    dialog.Filters.Clear
    dialog.Filters.Add "Excel Files", "*.xls; *.xlsx; *.xlsm"
'''
Analytics team can share multpiple multiple reports in a form of Excel file exported via DataGrip with automaticly automatically created 'script' worksheet.
VBA code is assigned to a button from Controls in the Developer tab.
<p align="center">
    <img src="https://github.com/user-attachments/assets/b77adab6-a219-4bd3-bad2-5230f550c89e" style="width: 35%;">
</p>

I have enabled the Microsoft ActiveX Data Objects with the MSDASQL provider, which acts as a bridge between OLE DB and ODBC.
<p align="center">
    <img src="https://github.com/user-attachments/assets/255d0912-4f0e-4c4e-b474-4338a56fc60d" style="width: 50%;">
</p>
The query results with headers are inserted, just below the trigger button, after cleaning the worksheet cells ensuring up to date values on read.
