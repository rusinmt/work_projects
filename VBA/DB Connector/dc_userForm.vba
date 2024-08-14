Option Explicit

Public UserName As String
Public Password As String
Public Cancelled As Boolean
  
Private Sub UserForm_Initialize()
    Me.Caption = "Login"
    TextBox1.Text = ""
    TextBox2.Text = ""
    TextBox2.PasswordChar = "*"
    Cancelled = True
End Sub
  
Private Sub CommandButton1_Click()
    If TextBox1.Text = "" Or TextBox2.Text = "" Then
        MsgBox "Enter username and password.", vbExclamation
        Exit Sub
    End If
    
    UserName = "pl." & TextBox1.Text
    Password = TextBox2.Text
    
    Cancelled = False
    Me.Hide
End Sub
          
Private Sub CommandButton2_Click()
    Cancelled = True
    Me.Hide
End Sub
