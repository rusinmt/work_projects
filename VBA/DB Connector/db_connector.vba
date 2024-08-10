Function OpenScript() As String
    Dim filePath As String
    Dim selectedWorkbook As Workbook
    Dim dialog As FileDialog
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim concatText As String
    Dim i As Long
    Dim cell As Range
    
    Set dialog = Application.FileDialog(msoFileDialogFilePicker)
    dialog.Title = "Select an Excel File"
    dialog.Filters.Clear
    dialog.Filters.Add "Excel Files", "*.xls; *.xlsx; *.xlsm"
    
    If dialog.Show = -1 Then
        filePath = dialog.SelectedItems(1)
        Set selectedWorkbook = Workbooks.Open(filePath, ReadOnly:=True)
        
        If WorksheetExists(selectedWorkbook, "script") Then
            Set ws = selectedWorkbook.Sheets("script")
            lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
            concatText = ""
        
            For i = 1 To lastRow
                Set cell = ws.Cells(i, 1)
                If Application.WorksheetFunction.IsText(cell.Value) Then
                    concatText = concatText & cell.Value & " "
                End If
            Next i
            concatText = Trim(concatText)
        Else
            MsgBox "The selected workbook does not contain a 'script'", vbExclamation
            concatText = ""
        End If
        
        selectedWorkbook.Close SaveChanges:=False
        OpenScript = concatText
    Else
        MsgBox "No file selected."
        OpenScript = ""
    End If
    Set dialog = Nothing
End Function
Function WorksheetExists(wb As Workbook, sheetName As String) As Boolean
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = wb.Sheets(sheetName)
    On Error GoTo 0
    WorksheetExists = Not ws Is Nothing
End Function
Sub DBconnect()
    Dim conn As ADODB.Connection
    Dim rs As ADODB.Recordset
    Dim connectionString As String
    Dim concatText As String
    Dim i As Long
    Dim targetSheet As Worksheet
  
    connectionString = "Provider=MSDASQL;" & _
        "Driver={PostgreSQL Unicode};" & _
        "Server= * " & _
        "Database= * ;" & _
        "UID= * ;" & _
        "PWD= * ;"
        
    Set conn = New ADODB.Connection
    conn.Open connectionString
    concatText = OpenScript()
    
    If concatText <> "" Then
        Set rs = conn.Execute(concatText)
        Set targetSheet = ThisWorkbook.Sheets("db_update")
        targetSheet.Cells.Clear
        
        For i = 0 To rs.Fields.Count - 1
            targetSheet.Cells(6, i + 1).Value = rs.Fields(i).Name
        Next i
        targetSheet.Range("A7").CopyFromRecordset rs
        Set DataRange = targetSheet.Range("A6").CurrentRegion
        Set tbl = targetSheet.ListObjects.Add(xlSrcRange, DataRange, , xlYes)
        tbl.TableStyle = "TableStyleLight1"
        
        rs.Close
        conn.Close
        Set rs = Nothing
        Set conn = Nothing
        
        MsgBox "Data updated successfully!", vbInformation
    Else
        MsgBox "No data to process", vbExclamation
    End If
End Sub
