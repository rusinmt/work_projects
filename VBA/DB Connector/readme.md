## Automate Database Updates with Excel VBA

I have developed an VBA solution offering a seamless way to connect to PostgreSQL database and retrieve data with minimal effort. A universal tool for managment without the nesesity of setting up a credential connection without a tool for querying. This provides up to date reads and combines the benefits of quick ad hoc analysis and visuals of Excel workbook. 

By selecting an Excel file containing an SQL query, from a pop up window, users can instantly access the database and import the results into the template workbook.
'''sql
Set dialog = Application.FileDialog(msoFileDialogFilePicker)
    dialog.Title = "Select an Excel File"
    dialog.Filters.Clear
    dialog.Filters.Add "Excel Files", "*.xls; *.xlsx; *.xlsm"
'''
Analytics team can share multpiple reports in a form of Excel file exported via DataGrip with automaticly created 'script' worksheet.

VBA code is assigned to a button from Controls in the Developer tab.
<p align="center">
    <img src="https://github.com/user-attachments/assets/b77adab6-a219-4bd3-bad2-5230f550c89e" style="width: 65%;">
</p>

![connect](https://github.com/user-attachments/assets/b77adab6-a219-4bd3-bad2-5230f550c89e)
