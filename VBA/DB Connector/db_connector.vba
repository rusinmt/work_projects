Public UserName As String
Public Password As String

Function ShowLoginForm() As Boolean
    Dim frmLogin As UserForm1
    Set frmLogin = New UserForm1
    frmLogin.Show
    
    If frmLogin.Cancelled Then
        MsgBox "Canceled.", vbInformation
        ShowLoginForm = False
    Else
        UserName = frmLogin.UserName
        Password = frmLogin.Password
        ShowLoginForm = True
    End If
    
    Unload frmLogin
    Set frmLogin = Nothing
End Function

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
            On Error Resume Next
            Set ws = selectedWorkbook.Sheets("Query")
            On Error GoTo 0
        End If
        
        If ws Is Nothing Then
            MsgBox "Please make sure the selected file contains a 'script' or 'Query' sheet or rename existing one.", vbExclamation
            concatText = ""
        Else
            lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
            concatText = ""
        
            For i = 1 To lastRow
                Set cell = ws.Cells(i, 1)
                If Application.WorksheetFunction.IsText(cell.Value) Then
                    If Not Trim(cell.Value) Like "--*" Then
                        concatText = concatText & Trim(cell.Value) & " "
                    End If
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
    Dim DataRange As Range
    Dim tbl As ListObject
    Dim i As Long
    Dim targetSheet As Worksheet
    Dim tableSheet As Worksheet
    
    If UserName = "" Or Password = "" Then
        If Not ShowLoginForm() Then
            MsgBox "Login cancelled. Cannot connect to the database.", vbExclamation
            Exit Sub
        End If
    End If
  
    connectionString = "Provider=MSDASQL;" & _
        "Driver={PostgreSQL Unicode};" & _
        "Server= server;" & _
        "Database= db;" & _
        "UID=" & UserName & ";" & _
        "PWD=" & Password & ";" & _
        "ConnectionTimeout=300;" & _
        "CommandTimeout=300"
        
    Set conn = New ADODB.Connection
    conn.Open connectionString
    conn.CommandTimeout = 300
    concatText = OpenScript()
    Set targetSheet = ThisWorkbook.Sheets("db_update")
    Set targetSheet = ThisWorkbook.Sheets("db_update")
        With targetSheet.Range("A6")
            .Value = concatText
            .Font.Color = RGB(255, 255, 255)
            .WrapText = False
            .RowHeight = targetSheet.StandardHeight
        End With
    
    If concatText <> "" Then
        Set rs = conn.Execute(concatText)
        On Error Resume Next
        Set tableSheet = ThisWorkbook.Worksheets("output")
        On Error GoTo 0
        
        If tableSheet Is Nothing Then
            Set tableSheet = ThisWorkbook.Worksheets.Add
            tableSheet.Name = "output"
            tableSheet.Move After:=ThisWorkbook.Sheets("db_update")
        Else
            tableSheet.Cells.Clear
        End If
        tableSheet.Activate
    
        For i = 0 To rs.Fields.Count - 1
            tableSheet.Cells(1, i + 1).Value = rs.Fields(i).Name
        Next i
        tableSheet.Range("A2").CopyFromRecordset rs
        Set DataRange = tableSheet.Range("A1").CurrentRegion
        Set tbl = tableSheet.ListObjects.Add(xlSrcRange, DataRange, , xlYes)
        tbl.TableStyle = "TableStyleLight1"
        tableSheet.UsedRange.Columns.AutoFit

        rs.Close
        conn.Close
        Set rs = Nothing
        Set conn = Nothing
        
        MsgBox "Data inserted successfully!", vbInformation
    End If
End Sub

Sub Refresh()
    Dim conn As ADODB.Connection
    Dim rs As ADODB.Recordset
    Dim connectionString As String
    Dim i As Long
    Dim targetSheet As Worksheet
    Dim tableSheet As Worksheet
    Dim DataRange As Range
    Dim tbl As ListObject
    Dim queryText As String
    
    Set targetSheet = ThisWorkbook.Sheets("db_update")
    queryText = targetSheet.Range("A6").Value
    
    If queryText = "" Then
        MsgBox "Extablish connection first, select 'Po³¹cz'.", vbInformation
        Exit Sub
    End If

    connectionString = "Provider=MSDASQL;" & _
        "Driver={PostgreSQL Unicode};" & _
        "Server= server;" & _
        "Database= db;" & _
        "UID=" & UserName & ";" & _
        "PWD=" & Password & ";" & _
        "ConnectionTimeout=300;" & _
        "CommandTimeout=300"

    Set conn = New ADODB.Connection
    conn.Open connectionString
    conn.CommandTimeout = 300
    
    Set tableSheet = ThisWorkbook.Sheets("output")
    Set rs = conn.Execute(queryText)
    tableSheet.Cells.Clear
    For i = 0 To rs.Fields.Count - 1
        tableSheet.Cells(1, i + 1).Value = rs.Fields(i).Name
    Next i
    tableSheet.Range("A2").CopyFromRecordset rs
    
    On Error Resume Next
    tableSheet.ListObjects(1).Unlist
    On Error GoTo 0
    
    Set DataRange = tableSheet.Range("A1").CurrentRegion
    Set tbl = tableSheet.ListObjects.Add(xlSrcRange, DataRange, , xlYes)
    tbl.TableStyle = "TableStyleLight1"
    tableSheet.UsedRange.Columns.AutoFit
    tableSheet.Activate
    
    rs.Close
    conn.Close
    Set rs = Nothing
    Set conn = Nothing
    
    MsgBox "Data updated successfully!", vbInformation
End Sub
