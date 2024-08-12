Function OpenScript() As String
    Dim filePath As String
    Dim selectedWorkbook As Workbook
    Dim dialog As FileDialog
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim concatText As String
    Dim i As Long
    Dim cell As Range
    Dim DataRange As Range
    Dim tbl As ListObject
    
    Set dialog = Application.FileDialog(msoFileDialogFilePicker)
    dialog.Title = "Select an Excel File"
    dialog.Filters.Clear
    dialog.Filters.Add "Excel Files", "*.xls; *.xlsx; *.xlsm"
    
    If dialog.Show = -1 Then
        filePath = dialog.SelectedItems(1)
        Set selectedWorkbook = Workbooks.Open(filePath, ReadOnly:=True)
        
        On Error Resume Next
        Set ws = selectedWorkbook.Sheets("script")
        On Error GoTo 0
        
        If ws Is Nothing Then
            MsgBox "Please make sure the selected file contains a 'script' sheet or rename existing one.", vbExclamation
            concatText = ""
        Else
            lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
            concatText = ""
        
            For i = 1 To lastRow
                Set cell = ws.Cells(i, 1)
                If Application.WorksheetFunction.IsText(cell.Value) Then
                    concatText = concatText & cell.Value & " "
                End If
            Next i
            concatText = Trim(concatText)
        End If
        
        selectedWorkbook.Close SaveChanges:=False
        OpenScript = concatText
    Else
        MsgBox "No file selected."
        OpenScript = ""
    End If
    Set dialog = Nothing
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
        "PWD= * ;" & _ 
        "ConnectionTimeout=300;" & _ 
        "CommandTimeout=300" ' Extending connection and query timeout for executing more complex queries.
        
    Set conn = New ADODB.Connection
    conn.Open connectionString
    conn.CommandTimeout = 300
    concatText = OpenScript()
    Set targetSheet = ThisWorkbook.Sheets("db_update")
    Set targetSheet = ThisWorkbook.Sheets("db_update")
        With targetSheet.Range("A1")
            .Value = concatText
            .Font.Color = RGB(255, 255, 255)
        End With
    
    If concatText <> "" Then
        Set rs = conn.Execute(concatText)
        targetSheet.Rows("2:" & targetSheet.Rows.Count).Clear
    
        For i = 0 To rs.Fields.Count - 1
            targetSheet.Cells(6, i + 1).Value = rs.Fields(i).Name
        Next i
        targetSheet.Range("A7").CopyFromRecordset rs
        Set DataRange = targetSheet.Range("A6").CurrentRegion
        Set tbl = targetSheet.ListObjects.Add(xlSrcRange, DataRange, , xlYes)
        tbl.TableStyle = "TableStyleLight1"
        targetSheet.UsedRange.Columns.AutoFit

        rs.Close
        conn.Close
        Set rs = Nothing
        Set conn = Nothing
        
        MsgBox "Data updated successfully!", vbInformation
    End If
End Sub

Sub Refresh()
    Dim conn As ADODB.Connection
    Dim rs As ADODB.Recordset
    Dim connectionString As String
    Dim i As Long
    Dim targetSheet As Worksheet
    Dim DataRange As Range
    Dim tbl As ListObject
    Dim queryText As String
    
    Set targetSheet = ThisWorkbook.Sheets("db_update")
    queryText = targetSheet.Range("A1").Value
    
    If queryText = "" Then
        MsgBox "Extablish connection first, select 'Connect'.", vbInformation
        Exit Sub
    End If

    connectionString = "Provider=MSDASQL;" & _
        "Driver={PostgreSQL Unicode};" & _
        "Server= * " & _
        "Database= * ;" & _
        "UID= * ;" & _
        "PWD= * ;" & _ 
        "ConnectionTimeout=300;" & _ 
        "CommandTimeout=300"

    Set conn = New ADODB.Connection
    conn.Open connectionString
    conn.CommandTimeout = 300
    
    Set rs = conn.Execute(queryText)
    targetSheet.Rows("2:" & targetSheet.Rows.Count).Clear
    For i = 0 To rs.Fields.Count - 1
        targetSheet.Cells(6, i + 1).Value = rs.Fields(i).Name
    Next i
    targetSheet.Range("A7").CopyFromRecordset rs
    
    On Error Resume Next
    targetSheet.ListObjects(1).Unlist
    On Error GoTo 0
    
    Set DataRange = targetSheet.Range("A6").CurrentRegion
    Set tbl = targetSheet.ListObjects.Add(xlSrcRange, DataRange, , xlYes)
    tbl.TableStyle = "TableStyleLight1"
    targetSheet.UsedRange.Columns.AutoFit
    
    rs.Close
    conn.Close
    Set rs = Nothing
    Set conn = Nothing
    
    MsgBox "Data updated successfully!", vbInformation
End Sub
