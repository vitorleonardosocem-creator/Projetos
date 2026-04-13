Imports System.Data.SqlClient
Imports System.IO
Imports System.Net.Mail
Imports System.Text.RegularExpressions
Imports Microsoft.Data.SqlClient

Public Class Lista_Individual
    ' Configurar conexão
    Dim conexao As String = "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"
    Dim registros As New DataTable()
    Dim indiceAtual As Integer = 0
    Dim pageSize As Integer = 20
    Dim currentPage As Integer = 1
    Dim totalRegistos As Integer = 0
    Private modoEdicao As Boolean = False
    Private almocoAntes As String = "Não" ' Guarda valor original para comparação

    Private Sub ListaComFoto_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        CarregarTotalRegistos()
        CarregarDados(currentPage, pageSize)
        MostrarRegistro(indiceAtual)
        BloquearCampos(True)
    End Sub

    ' Paginação - contar total de registos
    Private Sub CarregarTotalRegistos()
        Try
            Using conn As New SqlConnection(conexao)
                conn.Open()
                Dim cmd As New SqlCommand("SELECT COUNT(*) FROM Visitantes", conn)
                totalRegistos = CInt(cmd.ExecuteScalar())
            End Using
        Catch ex As Exception
            MessageBox.Show("Erro ao contar os registos: " & ex.Message)
        End Try
    End Sub

    ' Paginação - carregar uma página de registos
    Private Sub CarregarDados(pageNumber As Integer, pageSize As Integer)
        Try
            registros = New DataTable()
            Using conn As New SqlConnection(conexao)
                conn.Open()
                Dim cmd As New SqlCommand(
                    "SELECT Id, Nome, Empresa, Telefone, Email, Data, Responsavel, Observacao, PreConfirmado, Almoco
                    FROM
                        (SELECT ROW_NUMBER() OVER (ORDER BY Id) AS RowNum, * FROM Visitantes) t
                    WHERE RowNum BETWEEN @StartRow AND @EndRow
                    ORDER BY Id", conn)
                cmd.Parameters.Add("@StartRow", SqlDbType.Int).Value = ((pageNumber - 1) * pageSize) + 1
                cmd.Parameters.Add("@EndRow", SqlDbType.Int).Value = pageNumber * pageSize
                Dim adaptador As New SqlDataAdapter(cmd)
                adaptador.Fill(registros)
            End Using
            indiceAtual = 0
        Catch ex As Exception
            MessageBox.Show("Erro ao carregar os dados: " & ex.Message)
        End Try
    End Sub

    Private Sub BloquearCampos(bloquear As Boolean)
        txtNome.ReadOnly = bloquear
        txtEmpresa.ReadOnly = bloquear
        txtTelefone.ReadOnly = bloquear
        txtEmail.ReadOnly = bloquear
        txtResponsavel.ReadOnly = bloquear
        txtObservacao.ReadOnly = bloquear
        txtConfirmado.ReadOnly = bloquear
        txtAlmoco.ReadOnly = True ' Campo texto para mostrar apenas, não editável
        Date2.Enabled = Not bloquear
    End Sub

    Private Sub MostrarRegistro(indice As Integer)
        If registros.Rows.Count > 0 Then
            Dim linha As DataRow = registros.Rows(indice)
            txtID.Text = linha("Id").ToString()
            txtNome.Text = linha("Nome").ToString()
            txtEmpresa.Text = linha("Empresa").ToString()
            txtTelefone.Text = linha("Telefone").ToString()
            txtEmail.Text = linha("Email").ToString()
            If Not IsDBNull(linha("Data")) AndAlso Not String.IsNullOrEmpty(linha("Data").ToString()) Then
                Date2.Value = Convert.ToDateTime(linha("Data"))
            Else
                Date2.Value = DateTime.Now
            End If
            txtResponsavel.Text = linha("Responsavel").ToString()
            txtObservacao.Text = linha("Observacao").ToString()
            txtConfirmado.Text = linha("PreConfirmado").ToString()
            ' Atualiza o novo campo Almoco e guarda valor para comparação
            If Not IsDBNull(linha("Almoco")) Then
                txtAlmoco.Text = linha("Almoco").ToString()
                almocoAntes = txtAlmoco.Text
            Else
                txtAlmoco.Text = "Não Definido"
                almocoAntes = "Não"
            End If
        Else
            MessageBox.Show("Nenhum registro encontrado.")
        End If
    End Sub

    ' Validação dos campos obrigatórios e formatos
    Private Function ValidaCampos() As Boolean
        If String.IsNullOrWhiteSpace(txtNome.Text) Then
            MessageBox.Show("O campo Nome é obrigatório.")
            Return False
        End If
        If String.IsNullOrWhiteSpace(txtEmpresa.Text) Then
            MessageBox.Show("O campo Empresa é obrigatório.")
            Return False
        End If
        If Not Regex.IsMatch(txtEmail.Text, "^[a-zA-Z][\w\.-]*[a-zA-Z0-9]@[a-zA-Z0-9][\w\.-]*[a-zA-Z0-9]\.[a-zA-Z][a-zA-Z\.]*[a-zA-Z]$") Then
            MessageBox.Show("Introduza um email válido.")
            Return False
        End If
        If Not Regex.IsMatch(txtTelefone.Text, "^\d{9,15}$") Then
            MessageBox.Show("O telefone deve conter apenas números e ter entre 9 a 15 dígitos.")
            Return False
        End If
        Return True
    End Function

    Private Sub btnEsquerda_Click(sender As Object, e As EventArgs) Handles btnEsquerda.Click
        If indiceAtual > 0 Then
            indiceAtual -= 1
            MostrarRegistro(indiceAtual)
        ElseIf currentPage > 1 Then
            currentPage -= 1
            CarregarDados(currentPage, pageSize)
            MostrarRegistro(0)
        Else
            MessageBox.Show("Você está no primeiro registro.")
        End If
    End Sub

    Private Sub btnDireita_Click(sender As Object, e As EventArgs) Handles btnDireita.Click
        If indiceAtual < registros.Rows.Count - 1 Then
            indiceAtual += 1
            MostrarRegistro(indiceAtual)
        ElseIf (currentPage * pageSize) < totalRegistos Then
            currentPage += 1
            CarregarDados(currentPage, pageSize)
            MostrarRegistro(0)
        Else
            MessageBox.Show("Você está no último registro.")
        End If
    End Sub

    Private Sub btnEditar_Click(sender As Object, e As EventArgs) Handles btnEditar.Click
        If Not modoEdicao Then
            modoEdicao = True
            BloquearCampos(False)
            btnEditar.Text = "Gravar"
            ' Tornar txtAlmoco editável para alterar valor se necessário
            txtAlmoco.ReadOnly = False
        Else
            If Not ValidaCampos() Then Return
            Try
                Using conn As New SqlConnection(conexao)
                    conn.Open()
                    Dim query As String =
                        "UPDATE Visitantes SET Nome=@Nome, Empresa=@Empresa, Telefone=@Telefone, Email=@Email, Data=@Data, Responsavel=@Responsavel,
                         Observacao=@Observacao, PreConfirmado=@PreConfirmado, Almoco=@Almoco WHERE Id=@ID"
                    Using cmd As New SqlCommand(query, conn)
                        cmd.Parameters.Add("@Nome", SqlDbType.NVarChar, 100).Value = txtNome.Text
                        cmd.Parameters.Add("@Empresa", SqlDbType.NVarChar, 100).Value = txtEmpresa.Text
                        cmd.Parameters.Add("@Telefone", SqlDbType.NVarChar, 20).Value = txtTelefone.Text
                        cmd.Parameters.Add("@Email", SqlDbType.NVarChar, 100).Value = txtEmail.Text
                        cmd.Parameters.Add("@Data", SqlDbType.DateTime).Value = Date2.Value
                        cmd.Parameters.Add("@Responsavel", SqlDbType.NVarChar, 100).Value = txtResponsavel.Text
                        cmd.Parameters.Add("@Observacao", SqlDbType.NVarChar, 255).Value = txtObservacao.Text
                        cmd.Parameters.Add("@PreConfirmado", SqlDbType.NVarChar, 20).Value = txtConfirmado.Text
                        cmd.Parameters.Add("@Almoco", SqlDbType.NVarChar, 10).Value = txtAlmoco.Text
                        cmd.Parameters.Add("@ID", SqlDbType.Int).Value = Convert.ToInt32(txtID.Text)
                        cmd.ExecuteNonQuery()
                    End Using
                End Using

                ' Enviar e-mail se Almoco mudou de "Não" para "Sim"
                Dim almocoDepois As String = txtAlmoco.Text.Trim()
                If almocoAntes = "Não" AndAlso almocoDepois.Equals("Sim", StringComparison.OrdinalIgnoreCase) Then
                    Try
                        Dim mail As New MailMessage()
                        mail.From = New MailAddress("informatica@socem.pt")
                        mail.To.Add("Refeitorio@socem.pt")
                        mail.Subject = "Aviso: Acesso ao Almoço para Cliente"
                        mail.Body = $"O Cliente {txtNome.Text.Trim()} da empresa {txtEmpresa.Text.Trim()}, que vem acompanhado pelo responsável {txtResponsavel.Text.Trim()}, irá almoçar no dia {Date2.Value.ToShortDateString()}."
                        Dim smtp As New SmtpClient("smtp.office365.com")
                        smtp.Port = 587
                        smtp.Credentials = New System.Net.NetworkCredential("vitor.leonardo@socem.pt", "0L@cao1988")
                        smtp.EnableSsl = True
                        smtp.Send(mail)
                    Catch exMail As Exception
                        MessageBox.Show("Erro ao enviar email: " & exMail.Message, "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                    End Try
                End If

                MessageBox.Show("Dados atualizados com sucesso!", "Sucesso", MessageBoxButtons.OK, MessageBoxIcon.Information)
                modoEdicao = False
                BloquearCampos(True)
                btnEditar.Text = "Editar"
                txtAlmoco.ReadOnly = True
                ' Atualiza posição do registo atual usando seu ID
                Dim idAtual = txtID.Text
                CarregarDados(currentPage, pageSize)
                Dim index = 0
                For Each row As DataRow In registros.Rows
                    If row("Id").ToString = idAtual Then
                        indiceAtual = index
                        Exit For
                    End If
                    index += 1
                Next
                MostrarRegistro(indiceAtual)
                almocoAntes = almocoDepois ' Atualiza a variável para próxima edição
            Catch ex As Exception
                MessageBox.Show("Erro ao atualizar os dados: " & ex.Message, "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            End Try
        End If
    End Sub

    ' Outros menus e botões seguem inalterados (copiados do código original)
    Private Sub SairToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles SairToolStripMenuItem.Click
        Application.Exit()
    End Sub
    Private Sub GraficoEmpresasToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles GraficoEmpresasToolStripMenuItem.Click
        Dim frm As New Grafico_Empresas()
        frm.Show()
        Me.Close()
    End Sub
    Private Sub GraficoTotalVisitantesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles GraficoTotalVisitantesToolStripMenuItem.Click
        Dim frm As New Grafico_Total_Visitantes()
        frm.Show()
        Me.Close()
    End Sub
    Private Sub ListaToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaToolStripMenuItem.Click
        Dim frm As New ListaVisitantes()
        frm.Show()
        Me.Close()
    End Sub
    Private Sub ArovarOuRejeitarToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ArovarOuRejeitarToolStripMenuItem.Click
        Dim frm As New Aprovacao()
        frm.Show()
        Me.Close()
    End Sub
    Private Sub IrParaOMenuToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles IrParaOMenuToolStripMenuItem.Click
        Dim frm As New Menu()
        frm.Show()
        Me.Close()
    End Sub
    Private Sub ClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ClientesToolStripMenuItem.Click
        Dim frm As New InserirVisitantes()
        frm.Show()
        Me.Close()
    End Sub
    Private Sub Button1_Click(sender As Object, e As EventArgs) Handles Button1.Click
        If String.IsNullOrWhiteSpace(txtID.Text) Then
            MessageBox.Show("Nenhum registo selecionado para apagar.", "Atenção", MessageBoxButtons.OK, MessageBoxIcon.Warning)
            Return
        End If
        Dim confirmResult As DialogResult = MessageBox.Show(
            "Deseja realmente apagar este registo?",
            "Confirmação",
            MessageBoxButtons.YesNo,
            MessageBoxIcon.Question
        )
        If confirmResult = DialogResult.Yes Then
            Try
                Using conn As New SqlConnection(conexao)
                    conn.Open()
                    Dim cmd As New SqlCommand("DELETE FROM Visitantes WHERE Id = @ID", conn)
                    cmd.Parameters.Add("@ID", SqlDbType.Int).Value = Convert.ToInt32(txtID.Text)
                    Dim linhasAfetadas As Integer = cmd.ExecuteNonQuery()
                    If linhasAfetadas > 0 Then
                        MessageBox.Show("Registo apagado com sucesso.", "Sucesso", MessageBoxButtons.OK, MessageBoxIcon.Information)
                        CarregarTotalRegistos()
                        CarregarDados(currentPage, pageSize)
                        If registros.Rows.Count > 0 Then
                            indiceAtual = Math.Max(0, indiceAtual - 1)
                            MostrarRegistro(indiceAtual)
                        Else
                            LIMPAR_CAMPOS()
                        End If
                    Else
                        MessageBox.Show("Erro: Registo não foi encontrado/apagado.")
                    End If
                End Using
            Catch ex As Exception
                MessageBox.Show("Erro ao apagar registo: " & ex.Message, "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            End Try
        End If
    End Sub

    Private Sub LIMPAR_CAMPOS()
        txtID.Clear()
        txtNome.Clear()
        txtEmpresa.Clear()
        txtTelefone.Clear()
        txtEmail.Clear()
        txtResponsavel.Clear()
        txtObservacao.Clear()
        txtConfirmado.Clear()
        txtAlmoco.Clear()
        Date2.Value = DateTime.Now
    End Sub

    Private Sub btnDuplicar_Click(sender As Object, e As EventArgs) Handles btnDuplicar.Click
        Try
            If String.IsNullOrWhiteSpace(txtID.Text) Then
                MessageBox.Show("Nenhum registo selecionado para duplicar.", "Atenção", MessageBoxButtons.OK, MessageBoxIcon.Warning)
                Return
            End If
            Using conn As New SqlConnection(conexao)
                conn.Open()
                Dim query As String = "INSERT INTO Visitantes
                (Nome, Empresa, Telefone, Email, Data, Responsavel, Observacao, PreConfirmado, Almoco)
                VALUES (@Nome, @Empresa, @Telefone, @Email, @Data, @Responsavel, @Observacao, @PreConfirmado, @Almoco);
                SELECT CAST(SCOPE_IDENTITY() AS INT);"
                Using cmd As New SqlCommand(query, conn)
                    cmd.Parameters.Add("@Nome", SqlDbType.NVarChar, 100).Value = txtNome.Text
                    cmd.Parameters.Add("@Empresa", SqlDbType.NVarChar, 100).Value = txtEmpresa.Text
                    cmd.Parameters.Add("@Telefone", SqlDbType.NVarChar, 20).Value = txtTelefone.Text
                    cmd.Parameters.Add("@Email", SqlDbType.NVarChar, 100).Value = txtEmail.Text
                    cmd.Parameters.Add("@Data", SqlDbType.DateTime).Value = Date2.Value
                    cmd.Parameters.Add("@Responsavel", SqlDbType.NVarChar, 100).Value = txtResponsavel.Text
                    cmd.Parameters.Add("@Observacao", SqlDbType.NVarChar, 255).Value = txtObservacao.Text
                    cmd.Parameters.Add("@PreConfirmado", SqlDbType.NVarChar, 20).Value = txtConfirmado.Text
                    cmd.Parameters.Add("@Almoco", SqlDbType.NVarChar, 10).Value = txtAlmoco.Text
                    Dim novoID As Integer = CInt(cmd.ExecuteScalar())
                    MessageBox.Show("Registo duplicado! Edite e grave as alterações.", "Duplicação", MessageBoxButtons.OK, MessageBoxIcon.Information)
                    ' Recarregar o novo registo para permitir alterar antes de gravar
                    Using cmd2 As New SqlCommand("SELECT * FROM Visitantes WHERE Id = @ID", conn)
                        cmd2.Parameters.Add("@ID", SqlDbType.Int).Value = novoID
                        Using reader As SqlDataReader = cmd2.ExecuteReader()
                            If reader.Read() Then
                                txtID.Text = reader("Id").ToString()
                                txtNome.Text = reader("Nome").ToString()
                                txtEmpresa.Text = reader("Empresa").ToString()
                                txtTelefone.Text = reader("Telefone").ToString()
                                txtEmail.Text = reader("Email").ToString()
                                If Not IsDBNull(reader("Data")) AndAlso Not String.IsNullOrEmpty(reader("Data").ToString()) Then
                                    Date2.Value = Convert.ToDateTime(reader("Data"))
                                Else
                                    Date2.Value = DateTime.Now
                                End If
                                txtResponsavel.Text = reader("Responsavel").ToString()
                                txtObservacao.Text = reader("Observacao").ToString()
                                txtConfirmado.Text = reader("PreConfirmado").ToString()
                                If Not IsDBNull(reader("Almoco")) Then
                                    txtAlmoco.Text = reader("Almoco").ToString()
                                Else
                                    txtAlmoco.Text = "Não Definido"
                                End If
                            End If
                        End Using
                    End Using
                End Using
            End Using
            modoEdicao = True
            BloquearCampos(False)
            btnEditar.Text = "Gravar"
            txtAlmoco.ReadOnly = False
        Catch ex As Exception
            MessageBox.Show("Erro ao duplicar registo: " & ex.Message, "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    Private Sub ClientesToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles ClientesToolStripMenuItem1.Click
        Dim frm As New InserirVisitantesFornecedores()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaDeClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeClientesToolStripMenuItem.Click
        Dim frm As New Clientes()
        frm.Show()
        Me.Hide()
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

    Private Sub ListaDeClientesToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles ListaDeClientesToolStripMenuItem1.Click
        Dim frm As New ListaClientes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaDeVisitantesIndividualToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeVisitantesIndividualToolStripMenuItem.Click
        Dim frm As New Lista_Individual
        frm.Show()
        Close()
    End Sub

    Private Sub ListaDeVisitantesFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeVisitantesFornecedoresToolStripMenuItem.Click
        Dim frm As New ListaVisitantesFornecedores()
        frm.Show()
        Me.Hide()
    End Sub
End Class