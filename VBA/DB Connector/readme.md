## Automate Database Updates with Excel VBA

I have developed a VBA solution that offers a seamless way to connect to a PostgreSQL database and retrieve data with minimal effort.<br> A universal tool for managment without the use of any tool for querying. This provides up to date reads and combined with potential of ad hoc analysis and visuals of Excel workbook.

Firstly, the process requires the user to log in to the database within the created UserForm1 object by executing the dc_UserForm.vba procedures called upon in the ShowLoginForm() function from the main script.
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
Analytics team can share multpiple reports in a form of Excel file exported via DataGrip with automaticly automatically created 'Query' worksheet.
VBA code is assigned to a button from Controls in the Developer tab.
<p align="center">
    <img src="https://github.com/user-attachments/assets/b77adab6-a219-4bd3-bad2-5230f550c89e" style="width: 35%;">
</p>

I have enabled the Microsoft ActiveX Data Objects with the MSDASQL provider, which acts as a bridge between OLE DB and ODBC.
<p align="center">
    <img src="https://github.com/user-attachments/assets/255d0912-4f0e-4c4e-b474-4338a56fc60d" style="width: 50%;">
</p>
The query results with headers are inserted into the newly created "output" sheet. The code cleans the worksheet cells beforehand when the connection is established for the second time, to ensure up-to-date values are read. The code enables users to refresh the connected script with an additional "Refresh" button that uses the extracted query, stored in an unused cell of the workbook, in a similar fashion to the DBConnect procedure.

Some key fetaures:<br>
    - SQL queries can be extracted from Excel files from default DataGrip exports and files created internally from other sources named "script"<br>
    - OpenScript() returns lines that were not commented out:<br>
        ```sql
        If Not Trim(cell.Value) Like "--*" Then
            concatText = concatText & Trim(cell.Value) & " "
        End If
        ```
    - There are many exceptions informing the user about the execution of the program<br>
    - Extended connection and command timeouts were established for the Connection string:<br>
        ```sql
        "ConnectionTimeout=300;" & _
        "CommandTimeout=300"
        ```
    - Newly created result sheet is moved to the right of the db_connect sheet:<br>
        ```sql
        tableSheet.Move After:=ThisWorkbook.Sheets("db_update")
        ```
    - The "output" table is formatted and autofitted for better readability:<br>
        ```sql
        tbl.TableStyle = "TableStyleLight1"
        tableSheet.UsedRange.Columns.AutoFit
        ```
