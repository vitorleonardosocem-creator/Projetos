Imports System.Data.SqlClient
Imports System.Text.RegularExpressions
Imports Microsoft.Data.SqlClient

Public Class Fornecedores

    Private ReadOnly connString As String =
        "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"

    '======================== GRAVAR FORNECEDOR ========================

    Private Sub btnGravar_Click(sender As Object, e As EventArgs) Handles btnGravar.Click
        ' Normalizar texto (tirar espaços desnecessários)
        Dim nome As String = txtNome.Text.Trim()
        Dim empresa As String = txtEmpresa.Text.Trim()
        Dim telefoneTexto As String = txtTelefone.Text.Trim()
        Dim email As String = txtEmail.Text.Trim()

        ' 1. Validações básicas obrigatórias (Nome, Empresa, Telefone)
        If String.IsNullOrWhiteSpace(nome) OrElse
           String.IsNullOrWhiteSpace(empresa) OrElse
           String.IsNullOrWhiteSpace(telefoneTexto) Then

            MessageBox.Show("Por favor, preencha Nome, Empresa e Telefone.",
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        ' 2. Validação do telefone: apenas dígitos, sem espaços
        If Not Regex.IsMatch(telefoneTexto, "^\d+$") Then
            MessageBox.Show("O telefone deve conter apenas números (sem espaços).",
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        ' Para segurança, limitar a 18 dígitos (limite seguro de Long/BigInt)
        If telefoneTexto.Length > 18 Then
            MessageBox.Show("O telefone é demasiado longo.",
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        Dim telefoneNumero As Long
        If Not Long.TryParse(telefoneTexto, telefoneNumero) Then
            MessageBox.Show("O telefone é inválido.",
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        ' 3. Validação de email (opcional)
        Dim emailEhNull As Boolean = String.IsNullOrWhiteSpace(email)

        If Not emailEhNull Then
            Dim padraoEmail As String = "^[^@\s]+@[^@\s]+\.[^@\s]+$"
            If Not Regex.IsMatch(email, padraoEmail) Then
                MessageBox.Show("O email introduzido não é válido.",
                                "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                Exit Sub
            End If
        End If

        ' 4. Verificação de duplicata (Nome + Telefone iguais)
        Try
            Using connCheck As New SqlConnection(connString)
                connCheck.Open()

                Dim sqlCheck As String =
                    "SELECT COUNT(*) FROM Fornecedores WHERE Nome = @Nome AND Telefone = @Telefone"

                Using cmdCheck As New SqlCommand(sqlCheck, connCheck)
                    cmdCheck.Parameters.Add("@Nome", SqlDbType.NVarChar, 200).Value = nome
                    cmdCheck.Parameters.Add("@Telefone", SqlDbType.BigInt).Value = telefoneNumero

                    Dim count As Integer = Convert.ToInt32(cmdCheck.ExecuteScalar())

                    If count > 0 Then
                        MessageBox.Show("Este fornecedor já existe registado com o mesmo Nome e Telefone.",
                                        "Duplicado", MessageBoxButtons.OK, MessageBoxIcon.Warning)
                        Exit Sub
                    End If
                End Using
            End Using
        Catch ex As Exception
            MessageBox.Show("Erro ao verificar duplicatas: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End Try

        ' 5. Inserir na tabela Fornecedores
        Try
            Using conn As New SqlConnection(connString)
                conn.Open()

                Dim sql As String =
                    "INSERT INTO Fornecedores (Nome, Empresa, Telefone, Email) " &
                    "VALUES (@Nome, @Empresa, @Telefone, @Email);"

                Using cmd As New SqlCommand(sql, conn)
                    ' Nome
                    cmd.Parameters.Add("@Nome", SqlDbType.NVarChar, 200).Value = nome

                    ' Empresa
                    cmd.Parameters.Add("@Empresa", SqlDbType.NVarChar, 200).Value = empresa

                    ' Telefone
                    cmd.Parameters.Add("@Telefone", SqlDbType.BigInt).Value = telefoneNumero

                    ' Email (pode ser NULL)
                    Dim pEmail = cmd.Parameters.Add("@Email", SqlDbType.NVarChar, 255)
                    If emailEhNull Then
                        pEmail.Value = DBNull.Value
                    Else
                        pEmail.Value = email
                    End If

                    cmd.ExecuteNonQuery()
                End Using
            End Using

            MessageBox.Show("Fornecedor gravado com sucesso!",
                            "Sucesso", MessageBoxButtons.OK, MessageBoxIcon.Information)

            LimparCampos()

        Catch ex As Exception
            MessageBox.Show("Erro ao gravar Fornecedor: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    Private Sub LimparCampos()
        txtNome.Clear()
        txtEmpresa.Clear()
        txtTelefone.Clear()
        txtEmail.Clear()
        txtNome.Focus()
    End Sub

    '======================== MENUS / NAVEGAÇÃO ========================

    Private Sub MenuToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles MenuToolStripMenuItem.Click
        ' Sem ação específica (placeholder para o menu)
    End Sub

    Private Sub IrParaOMenuToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles IrParaOMenuToolStripMenuItem.Click
        Dim frm As New Menu()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub SairToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles SairToolStripMenuItem.Click
        Application.Exit()
    End Sub

    Private Sub GraficosToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles GraficosToolStripMenuItem.Click
        Dim frm As New Grafico_Empresas()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub GraficoTotalVisitantesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles GraficoTotalVisitantesToolStripMenuItem.Click
        Dim frm As New Grafico_Total_Visitantes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaToolStripMenuItem.Click
        Dim frm As New ListaVisitantes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaComFotoToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaComFotoToolStripMenuItem.Click
        Dim frm As New Lista_Individual()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub TEsteToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles TEsteToolStripMenuItem1.Click
        Dim frm As New InserirVisitantes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaDeClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeClientesToolStripMenuItem.Click
        Dim frm As New ListaClientes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub Fornecedores_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        ' Código de inicialização, se necessário
    End Sub

    Private Sub InserirFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles InserirFornecedoresToolStripMenuItem.Click
        Dim frm As New Fornecedores()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaDeFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeFornecedoresToolStripMenuItem.Click
        Dim frm As New ListaFornecedores()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub InserirClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles InserirClientesToolStripMenuItem.Click
        Dim frm As New Clientes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub VisitasFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles VisitasFornecedoresToolStripMenuItem.Click
        Dim frm As New InserirVisitantesFornecedores()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaDeVisitantesFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeVisitantesFornecedoresToolStripMenuItem.Click
        Dim frm As New ListaVisitantesFornecedores()
        frm.Show()
        Me.Hide()
    End Sub
End Class
