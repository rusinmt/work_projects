## Form guidence

As part of a larger automation tool, I have developed a VBA subroutine to assist users in entering information accurately. 
```vba
Option Explicit

Private Sub Worksheet_Change(ByVal Target As Range)
    Dim cell As Range
    For Each cell In Target.Cells
        Select Case cell.Value
            Case "id"
                FormatCell cell
            Case "number"
                FormatCell cell
            Case ""
                If Range("A1").Value = "" Then Range("A1").Value = "id"
                If Range("B1").Value = "" Then Range("B1").Value = "number"
            Case Else
                cell.Font.Color = &H0
        End Select
    Next cell
End Sub

Private Sub Worksheet_BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)
    Target.Value = ""
End Sub

Private Sub FormatCell(ByVal Target As Range)
    Target.Font.Color = &H808080
End Sub
```
This subroutine automatically populates cells with placeholder when they are left empty.
