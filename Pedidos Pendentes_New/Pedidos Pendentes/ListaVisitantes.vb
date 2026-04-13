Imports System.Data.SqlClient
Imports System.Drawing.Printing
Imports System.IO
Imports System.Net.Mail
Imports Microsoft.Data.SqlClient
Imports Excel = Microsoft.Office.Interop.Excel
Imports System.Threading.Tasks

Public Class ListaVisitantes
    ' Variáveis globais para armazenar dados do visitante
    Private nomeVisitante As String
    Private empresaVisitante As String
    Private telefoneVisitante As String
    Private emailVisitante As String
    Private fotoVisitante As Byte()
    Private lblCabecalho As Label
    Private panelFiltro As Panel

    ' Variáveis para paginação
    Private paginaAtual As Integer = 1
    Private totalRegistros As Integer = 0
    Private registrosPorPagina As Integer = 20

    ' Variável para filtro de nome ou empresa
    Private filtroNomeEmpresa As String = ""

    ' Controles para paginação
    Private WithEvents btnPrimeiro As Button
    Private WithEvents btnAnterior As Button
    Private WithEvents btnProximo As Button
    Private WithEvents btnUltimo As Button

    Private lblPagina As Label

    Private Async Sub ListaVisitantes_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        AdicionarCabecalho()
        AdicionarFiltroNoDataGridView()
        InicializarColunasAcoes()
        InicializarControlesPaginacao()

        dgvVisitantes.Location = New Point(10, panelFiltro.Bottom + 50)
        dgvVisitantes.Size = New Size(Me.ClientSize.Width - 20, Me.ClientSize.Height - panelFiltro.Bottom - 60)
        dgvVisitantes.Anchor = AnchorStyles.Top Or AnchorStyles.Left Or AnchorStyles.Right Or AnchorStyles.Bottom
        dgvVisitantes.ColumnHeadersHeight = 48
        dgvVisitantes.ColumnHeadersDefaultCellStyle.Font = New Font("Segoe UI", 12, FontStyle.Bold)
        AddHandler dgvVisitantes.CellContentClick, AddressOf dgvVisitantes_CellContentClick

        totalRegistros = Await ObterTotalRegistrosAsync(filtroNomeEmpresa)
        Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
        AtualizarLabelPagina()
    End Sub

    Private Sub AdicionarCabecalho()
        If lblCabecalho Is Nothing Then
            lblCabecalho = New Label()
            lblCabecalho.Text = "LISTA DE VISITANTES"
            lblCabecalho.Size = New Size(Me.ClientSize.Width - 20, 38)
            lblCabecalho.Location = New Point(10, 25)
            lblCabecalho.Font = New Font("Segoe UI", 14, FontStyle.Bold)
            lblCabecalho.TextAlign = ContentAlignment.MiddleCenter
            lblCabecalho.BackColor = Color.LightSkyBlue
            lblCabecalho.ForeColor = Color.Black
            lblCabecalho.Anchor = AnchorStyles.Top Or AnchorStyles.Left Or AnchorStyles.Right
            lblCabecalho.BorderStyle = BorderStyle.FixedSingle
            Me.Controls.Add(lblCabecalho)
            lblCabecalho.BringToFront()
        End If
    End Sub

    Private Sub AdicionarFiltroNoDataGridView()
        If panelFiltro Is Nothing Then
            panelFiltro = New Panel()
            panelFiltro.Size = New Size(Me.ClientSize.Width - 20, 36)
            panelFiltro.Location = New Point(10, lblCabecalho.Bottom + 10)
            panelFiltro.Anchor = AnchorStyles.Top Or AnchorStyles.Left Or AnchorStyles.Right
            panelFiltro.BackColor = SystemColors.Control

            Dim txtFiltro As New TextBox()
            txtFiltro.PlaceholderText = "Pesquisar por nome ou empresa..."
            txtFiltro.Width = 250
            txtFiltro.Location = New Point(10, 6)
            txtFiltro.TextAlign = HorizontalAlignment.Left
            AddHandler txtFiltro.TextChanged, AddressOf FiltrarDados

            panelFiltro.Controls.Add(txtFiltro)
            Me.Controls.Add(panelFiltro)
            panelFiltro.BringToFront()
        End If
    End Sub

    Private Sub InicializarColunasAcoes()
        If dgvVisitantes.Columns.Contains("Editar") = False Then
            Dim btnEditar As New DataGridViewButtonColumn()
            btnEditar.Name = "Editar"
            btnEditar.HeaderText = ""
            btnEditar.Text = "Editar"
            btnEditar.UseColumnTextForButtonValue = True
            dgvVisitantes.Columns.Add(btnEditar)
        End If

        ' Mantém o código da coluna Duplicar mas vamos escondê-la
        If dgvVisitantes.Columns.Contains("Duplicar") = False Then
            Dim btnDuplicar As New DataGridViewButtonColumn()
            btnDuplicar.Name = "Duplicar"
            btnDuplicar.HeaderText = ""
            btnDuplicar.Text = "Duplicar"
            btnDuplicar.UseColumnTextForButtonValue = True
            dgvVisitantes.Columns.Add(btnDuplicar)
        End If

        If dgvVisitantes.Columns.Contains("Eliminar") = False Then
            Dim btnEliminar As New DataGridViewButtonColumn()
            btnEliminar.Name = "Eliminar"
            btnEliminar.HeaderText = ""
            btnEliminar.Text = "Eliminar"
            btnEliminar.UseColumnTextForButtonValue = True
            dgvVisitantes.Columns.Add(btnEliminar)
        End If

        ' Garante que a coluna Duplicar está invisível
        If dgvVisitantes.Columns.Contains("Duplicar") Then
            dgvVisitantes.Columns("Duplicar").Visible = False
        End If
    End Sub

    Private Sub InicializarControlesPaginacao()
        If btnPrimeiro Is Nothing Then
            btnPrimeiro = New Button()
            btnPrimeiro.Text = "Primeiro"
            btnPrimeiro.Size = New Size(75, 25)
            btnPrimeiro.Location = New Point(10, panelFiltro.Bottom + 10)
            btnPrimeiro.Anchor = AnchorStyles.Left Or AnchorStyles.Top
            AddHandler btnPrimeiro.Click, AddressOf btnPrimeiro_Click
            Me.Controls.Add(btnPrimeiro)
            btnPrimeiro.BringToFront()
        End If

        If btnAnterior Is Nothing Then
            btnAnterior = New Button()
            btnAnterior.Text = "Anterior"
            btnAnterior.Size = New Size(75, 25)
            btnAnterior.Location = New Point(100, panelFiltro.Bottom + 10)
            btnAnterior.Anchor = AnchorStyles.Left Or AnchorStyles.Top
            AddHandler btnAnterior.Click, AddressOf btnAnterior_Click
            Me.Controls.Add(btnAnterior)
            btnAnterior.BringToFront()
        End If

        If btnProximo Is Nothing Then
            btnProximo = New Button()
            btnProximo.Text = "Próximo"
            btnProximo.Size = New Size(75, 25)
            btnProximo.Location = New Point(190, panelFiltro.Bottom + 10)
            btnProximo.Anchor = AnchorStyles.Left Or AnchorStyles.Top
            AddHandler btnProximo.Click, AddressOf btnProximo_Click
            Me.Controls.Add(btnProximo)
            btnProximo.BringToFront()
        End If

        If btnUltimo Is Nothing Then
            btnUltimo = New Button()
            btnUltimo.Text = "Último"
            btnUltimo.Size = New Size(75, 25)
            btnUltimo.Location = New Point(280, panelFiltro.Bottom + 10)
            btnUltimo.Anchor = AnchorStyles.Left Or AnchorStyles.Top
            AddHandler btnUltimo.Click, AddressOf btnUltimo_Click
            Me.Controls.Add(btnUltimo)
            btnUltimo.BringToFront()
        End If

        If lblPagina Is Nothing Then
            lblPagina = New Label()
            lblPagina.Size = New Size(150, 25)
            lblPagina.Location = New Point(370, panelFiltro.Bottom + 10)
            lblPagina.Anchor = AnchorStyles.Left Or AnchorStyles.Top
            Me.Controls.Add(lblPagina)
            lblPagina.BringToFront()
        End If
    End Sub

    Private Async Sub btnPrimeiro_Click(sender As Object, e As EventArgs)
        If paginaAtual <> 1 Then
            paginaAtual = 1
            Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
            AtualizarLabelPagina()
        End If
    End Sub

    Private Async Sub btnAnterior_Click(sender As Object, e As EventArgs)
        If paginaAtual > 1 Then
            paginaAtual -= 1
            Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
            AtualizarLabelPagina()
        End If
    End Sub

    Private Async Sub btnUltimo_Click(sender As Object, e As EventArgs)
        Dim totalPaginas As Integer = Math.Ceiling(totalRegistros / registrosPorPagina)
        If paginaAtual <> totalPaginas Then
            paginaAtual = totalPaginas
            Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
            AtualizarLabelPagina()
        End If
    End Sub

    Private Async Sub btnProximo_Click(sender As Object, e As EventArgs)
        Dim totalPaginas As Integer = Math.Ceiling(totalRegistros / registrosPorPagina)
        If paginaAtual < totalPaginas Then
            paginaAtual += 1
            Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
            AtualizarLabelPagina()
        End If
    End Sub

    Private Sub AtualizarLabelPagina()
        Dim totalPaginas As Integer = Math.Ceiling(totalRegistros / registrosPorPagina)
        lblPagina.Text = $"Página {paginaAtual} de {totalPaginas}"
    End Sub

    Private Async Function ObterTotalRegistrosAsync(Optional filtro As String = "") As Task(Of Integer)
        Dim conexao As String = "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"
        Dim query As String = "SELECT COUNT(*) FROM Visitantes WHERE Nome LIKE @Filtro OR Empresa LIKE @Filtro"
        Using conn As New SqlConnection(conexao)
            Using cmd As New SqlCommand(query, conn)
                cmd.Parameters.AddWithValue("@Filtro", "%" & filtro & "%")
                Await conn.OpenAsync()
                Return Convert.ToInt32(Await cmd.ExecuteScalarAsync())
            End Using
        End Using
    End Function

    Private Async Function CarregarDadosPaginaAsync(pagina As Integer, Optional filtro As String = "") As Task
        Dim conexao As String = "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"
        Dim offset As Integer = (pagina - 1) * registrosPorPagina
        Dim query As String = "SELECT Id, Nome, Empresa, Telefone, Email, Data, Responsavel, Observacao, PreConfirmado, Almoco " &
                              "FROM Visitantes WHERE Nome LIKE @Filtro OR Empresa LIKE @Filtro " &
                              "ORDER BY Data DESC OFFSET @Offset ROWS FETCH NEXT @Limite ROWS ONLY"
        Try
            Using conn As New SqlConnection(conexao)
                Using cmd As New SqlCommand(query, conn)
                    cmd.Parameters.AddWithValue("@Filtro", "%" & filtro & "%")
                    cmd.Parameters.AddWithValue("@Offset", offset)
                    cmd.Parameters.AddWithValue("@Limite", registrosPorPagina)
                    Dim adapter As New SqlDataAdapter(cmd)
                    Dim tabela As New DataTable()
                    Await conn.OpenAsync()
                    Await Task.Run(Sub() adapter.Fill(tabela))
                    dgvVisitantes.DataSource = tabela

                    If dgvVisitantes.Columns.Contains("Id") Then dgvVisitantes.Columns("Id").Visible = False
                    If dgvVisitantes.Columns.Contains("Nome") Then dgvVisitantes.Columns("Nome").HeaderText = "Nome do Visitante"
                    If dgvVisitantes.Columns.Contains("Empresa") Then dgvVisitantes.Columns("Empresa").HeaderText = "Empresa"
                    If dgvVisitantes.Columns.Contains("Telefone") Then dgvVisitantes.Columns("Telefone").HeaderText = "Telefone"
                    If dgvVisitantes.Columns.Contains("Email") Then dgvVisitantes.Columns("Email").HeaderText = "Email"
                    If dgvVisitantes.Columns.Contains("Data") Then dgvVisitantes.Columns("Data").HeaderText = "Data"
                    If dgvVisitantes.Columns.Contains("Responsavel") Then dgvVisitantes.Columns("Responsavel").HeaderText = "Responsável"
                    If dgvVisitantes.Columns.Contains("Observacao") Then dgvVisitantes.Columns("Observacao").HeaderText = "Observação"
                    If dgvVisitantes.Columns.Contains("PreConfirmado") Then dgvVisitantes.Columns("PreConfirmado").HeaderText = "Pré-Confirmado"
                    If dgvVisitantes.Columns.Contains("Almoco") Then dgvVisitantes.Columns("Almoco").HeaderText = "Almoço"

                    ' ==== ORDEM DAS COLUNAS ====
                    If dgvVisitantes.Columns.Contains("Nome") Then dgvVisitantes.Columns("Nome").DisplayIndex = 0
                    If dgvVisitantes.Columns.Contains("Empresa") Then dgvVisitantes.Columns("Empresa").DisplayIndex = 1
                    If dgvVisitantes.Columns.Contains("Telefone") Then dgvVisitantes.Columns("Telefone").DisplayIndex = 2
                    If dgvVisitantes.Columns.Contains("Email") Then dgvVisitantes.Columns("Email").DisplayIndex = 3
                    If dgvVisitantes.Columns.Contains("Data") Then dgvVisitantes.Columns("Data").DisplayIndex = 4
                    If dgvVisitantes.Columns.Contains("Responsavel") Then dgvVisitantes.Columns("Responsavel").DisplayIndex = 5
                    If dgvVisitantes.Columns.Contains("Observacao") Then dgvVisitantes.Columns("Observacao").DisplayIndex = 6
                    If dgvVisitantes.Columns.Contains("PreConfirmado") Then dgvVisitantes.Columns("PreConfirmado").DisplayIndex = 7
                    If dgvVisitantes.Columns.Contains("Almoco") Then dgvVisitantes.Columns("Almoco").DisplayIndex = 8

                    Dim totalCols = dgvVisitantes.Columns.Count

                    If dgvVisitantes.Columns.Contains("Editar") Then dgvVisitantes.Columns("Editar").DisplayIndex = totalCols - 3
                    If dgvVisitantes.Columns.Contains("Duplicar") Then
                        ' Mantém a posição mas garante que está invisível
                        dgvVisitantes.Columns("Duplicar").DisplayIndex = totalCols - 2
                        dgvVisitantes.Columns("Duplicar").Visible = False
                    End If
                    If dgvVisitantes.Columns.Contains("Eliminar") Then dgvVisitantes.Columns("Eliminar").DisplayIndex = totalCols - 1
                End Using
            End Using
        Catch ex As Exception
            MessageBox.Show("Erro ao carregar os dados: " & ex.Message)
        End Try
    End Function

    Private Async Sub FiltrarDados(sender As Object, e As EventArgs)
        Dim txtFiltro As TextBox = CType(sender, TextBox)
        filtroNomeEmpresa = txtFiltro.Text.Trim()
        paginaAtual = 1
        totalRegistros = Await ObterTotalRegistrosAsync(filtroNomeEmpresa)
        Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
        AtualizarLabelPagina()
    End Sub

    Private Sub dgvVisitantes_CellContentClick(sender As Object, e As DataGridViewCellEventArgs)
        If e.RowIndex < 0 Then Return
        Dim coluna = dgvVisitantes.Columns(e.ColumnIndex).Name
        If coluna = "Editar" Then
            EditarVisitanteAsync(e.RowIndex)
        ElseIf coluna = "Duplicar" Then
            ' Coluna existe mas está invisível, e o clique é ignorado para evitar erros dos colaboradores.
            Return
        ElseIf coluna = "Eliminar" Then
            EliminarVisitanteAsync(e.RowIndex)
        End If
    End Sub

    Private Async Sub EditarVisitanteAsync(rowIndex As Integer)
        Dim tabela As DataTable = TryCast(dgvVisitantes.DataSource, DataTable)
        If tabela Is Nothing Then Return
        Dim rowView As DataRowView = CType(dgvVisitantes.Rows(rowIndex).DataBoundItem, DataRowView)
        Dim linha As DataRow = rowView.Row
        Using frmEdicao As New Form()
            frmEdicao.Text = "Editar Visitante"
            frmEdicao.Size = New Size(400, 470)
            frmEdicao.FormBorderStyle = FormBorderStyle.FixedDialog
            frmEdicao.MaximizeBox = False
            frmEdicao.MinimizeBox = False
            frmEdicao.StartPosition = FormStartPosition.CenterParent

            Dim txtNome As New TextBox() With {.Left = 130, .Top = 20, .Width = 200, .Text = linha("Nome").ToString()}
            Dim txtEmpresa As New TextBox() With {.Left = 130, .Top = 60, .Width = 200, .Text = linha("Empresa").ToString()}
            Dim txtTelefone As New TextBox() With {.Left = 130, .Top = 100, .Width = 200, .Text = linha("Telefone").ToString()}
            Dim txtEmail As New TextBox() With {.Left = 130, .Top = 140, .Width = 200, .Text = linha("Email").ToString()}
            Dim pickerData As New DateTimePicker() With {.Left = 130, .Top = 180, .Width = 200, .Value = Convert.ToDateTime(linha("Data"))}
            Dim txtResponsavel As New TextBox() With {.Left = 130, .Top = 220, .Width = 200, .Text = linha("Responsavel").ToString()}
            Dim txtObservacao As New TextBox() With {.Left = 130, .Top = 260, .Width = 200, .Text = linha("Observacao").ToString()}
            Dim cmbPreConfirmado As New ComboBox() With {.Left = 130, .Top = 300, .Width = 200, .DropDownStyle = ComboBoxStyle.DropDownList}
            cmbPreConfirmado.Items.AddRange(New String() {"SIM", "NAO"})
            cmbPreConfirmado.SelectedItem = linha("PreConfirmado").ToString()
            Dim cmbAlmoco As New ComboBox() With {.Left = 130, .Top = 340, .Width = 200}
            cmbAlmoco.Items.AddRange(New String() {"Sim", "Não"})
            cmbAlmoco.DropDownStyle = ComboBoxStyle.DropDownList
            cmbAlmoco.SelectedItem = linha("Almoco").ToString()

            frmEdicao.Controls.AddRange({
                New Label() With {.Text = "Nome:", .Left = 20, .Top = 20, .Width = 100},
                txtNome,
                New Label() With {.Text = "Empresa:", .Left = 20, .Top = 60, .Width = 100},
                txtEmpresa,
                New Label() With {.Text = "Telefone:", .Left = 20, .Top = 100, .Width = 100},
                txtTelefone,
                New Label() With {.Text = "Email:", .Left = 20, .Top = 140, .Width = 100},
                txtEmail,
                New Label() With {.Text = "Data:", .Left = 20, .Top = 180, .Width = 100},
                pickerData,
                New Label() With {.Text = "Responsável:", .Left = 20, .Top = 220, .Width = 100},
                txtResponsavel,
                New Label() With {.Text = "Observação:", .Left = 20, .Top = 260, .Width = 100},
                txtObservacao,
                New Label() With {.Text = "Pré-Confirmado:", .Left = 20, .Top = 300, .Width = 100},
                cmbPreConfirmado,
                New Label() With {.Text = "Almoço:", .Left = 20, .Top = 340, .Width = 100},
                cmbAlmoco
                })

            Dim btnGravar As New Button() With {.Text = "Gravar", .Left = 130, .Top = 410, .Width = 100}
            AddHandler btnGravar.Click,
                Async Sub()
                    Dim idVisitante As Integer = Convert.ToInt32(linha("Id"))
                    Dim almocoAntes As String = linha("Almoco").ToString()
                    Dim almocoDepois As String = cmbAlmoco.SelectedItem.ToString()
                    Try
                        Using conn As New SqlConnection("Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;")
                            Await conn.OpenAsync()
                            Dim query As String = "UPDATE Visitantes SET Nome=@Nome, Empresa=@Empresa, Telefone=@Telefone, Email=@Email, Data=@Data, Responsavel=@Responsavel, Observacao=@Observacao, PreConfirmado=@PreConfirmado, Almoco=@Almoco WHERE Id=@Id"
                            Using cmd As New SqlCommand(query, conn)
                                cmd.Parameters.AddWithValue("@Nome", txtNome.Text)
                                cmd.Parameters.AddWithValue("@Empresa", txtEmpresa.Text)
                                cmd.Parameters.AddWithValue("@Telefone", txtTelefone.Text)
                                cmd.Parameters.AddWithValue("@Email", txtEmail.Text)
                                cmd.Parameters.AddWithValue("@Data", pickerData.Value)
                                cmd.Parameters.AddWithValue("@Responsavel", txtResponsavel.Text)
                                cmd.Parameters.AddWithValue("@Observacao", txtObservacao.Text)
                                cmd.Parameters.AddWithValue("@PreConfirmado", cmbPreConfirmado.SelectedItem.ToString())
                                cmd.Parameters.AddWithValue("@Almoco", almocoDepois)
                                cmd.Parameters.AddWithValue("@Id", idVisitante)
                                Await cmd.ExecuteNonQueryAsync()
                            End Using
                        End Using

                        If almocoAntes = "Não" AndAlso almocoDepois.Equals("Sim", StringComparison.OrdinalIgnoreCase) Then
                            Try
                                Dim mail As New MailMessage()
                                mail.From = New MailAddress("informatica@socem.pt")
                                mail.To.Add("Refeitorio@socem.pt")
                                mail.Subject = "Aviso: Acesso ao Almoço para Cliente"
                                mail.Body = $"O Cliente {txtNome.Text.Trim()} da empresa {txtEmpresa.Text.Trim()}, que vem acompanhado pelo responsável {txtResponsavel.Text.Trim()}, irá almoçar no dia {pickerData.Value.ToShortDateString()}."
                                Dim smtp As New SmtpClient("smtp.office365.com")
                                smtp.Port = 587
                                smtp.Credentials = New System.Net.NetworkCredential("vitor.leonardo@socem.pt", "0L@cao1988")
                                smtp.EnableSsl = True
                                smtp.Send(mail)
                            Catch exMail As Exception
                                MessageBox.Show("Erro ao enviar email: " & exMail.Message, "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                            End Try
                        End If

                        frmEdicao.DialogResult = DialogResult.OK
                    Catch ex As Exception
                        MessageBox.Show("Erro ao gravar alterações: " & ex.Message)
                    End Try
                End Sub

            frmEdicao.Controls.Add(btnGravar)
            If frmEdicao.ShowDialog() = DialogResult.OK Then
                Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
                AtualizarLabelPagina()
            End If
        End Using
    End Sub

    Private Async Sub DuplicarVisitanteAsync(rowIndex As Integer)
        ' Função mantida para compatibilidade, mas não é mais chamada pela UI.
        Dim tabela As DataTable = TryCast(dgvVisitantes.DataSource, DataTable)
        If tabela Is Nothing Then Return
        Dim rowView As DataRowView = CType(dgvVisitantes.Rows(rowIndex).DataBoundItem, DataRowView)
        Dim linha As DataRow = rowView.Row
        Try
            Using conn As New SqlConnection("Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;")
                Await conn.OpenAsync()
                Dim query As String =
                    "INSERT INTO Visitantes (Nome, Empresa, Telefone, Email, Data, Responsavel, Observacao, PreConfirmado, Almoco) " &
                    "VALUES (@Nome, @Empresa, @Telefone, @Email, @Data, @Responsavel, @Observacao, @PreConfirmado, @Almoco)"
                Using cmd As New SqlCommand(query, conn)
                    cmd.Parameters.AddWithValue("@Nome", linha("Nome").ToString())
                    cmd.Parameters.AddWithValue("@Empresa", linha("Empresa").ToString())
                    cmd.Parameters.AddWithValue("@Telefone", linha("Telefone").ToString())
                    cmd.Parameters.AddWithValue("@Email", linha("Email").ToString())
                    cmd.Parameters.AddWithValue("@Data", Convert.ToDateTime(linha("Data")))
                    cmd.Parameters.AddWithValue("@Responsavel", linha("Responsavel").ToString())
                    cmd.Parameters.AddWithValue("@Observacao", linha("Observacao").ToString())
                    cmd.Parameters.AddWithValue("@PreConfirmado", linha("PreConfirmado").ToString())
                    cmd.Parameters.AddWithValue("@Almoco", linha("Almoco").ToString())
                    Await cmd.ExecuteNonQueryAsync()
                End Using
            End Using
            MessageBox.Show("Registo duplicado com sucesso!")
            totalRegistros = Await ObterTotalRegistrosAsync(filtroNomeEmpresa)
            Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
            AtualizarLabelPagina()
        Catch ex As Exception
            MessageBox.Show("Erro ao duplicar registo: " & ex.Message)
        End Try
    End Sub

    Private Async Sub EliminarVisitanteAsync(rowIndex As Integer)
        Dim tabela As DataTable = TryCast(dgvVisitantes.DataSource, DataTable)
        If tabela Is Nothing Then Return
        Dim rowView As DataRowView = CType(dgvVisitantes.Rows(rowIndex).DataBoundItem, DataRowView)
        Dim linha As DataRow = rowView.Row
        Dim idVisitante As Integer = Convert.ToInt32(linha("Id"))
        Dim confirmResult As DialogResult = MessageBox.Show("Confirmar eliminação do registo?", "Atenção", MessageBoxButtons.YesNo, MessageBoxIcon.Warning)
        If confirmResult = DialogResult.Yes Then
            Try
                Using conn As New SqlConnection("Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;")
                    Await conn.OpenAsync()
                    Dim query As String = "DELETE FROM Visitantes WHERE Id = @Id"
                    Using cmd As New SqlCommand(query, conn)
                        cmd.Parameters.AddWithValue("@Id", idVisitante)
                        Await cmd.ExecuteNonQueryAsync()
                    End Using
                End Using
                MessageBox.Show("Registo eliminado com sucesso.")
                totalRegistros = Await ObterTotalRegistrosAsync(filtroNomeEmpresa)
                Dim totalPaginas As Integer = Math.Ceiling(totalRegistros / registrosPorPagina)
                If paginaAtual > totalPaginas And paginaAtual > 1 Then paginaAtual -= 1
                Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
                AtualizarLabelPagina()
            Catch ex As Exception
                MessageBox.Show("Erro ao eliminar registo: " & ex.Message)
            End Try
        End If
    End Sub

    Private Sub PrintFicha()
        If dgvVisitantes.SelectedRows.Count > 0 Then
            Dim selectedRow As DataGridViewRow = dgvVisitantes.SelectedRows(0)
            nomeVisitante = If(selectedRow.Cells("Nome").Value, "").ToString()
            empresaVisitante = If(selectedRow.Cells("Empresa").Value, "").ToString()
            telefoneVisitante = If(selectedRow.Cells("Telefone").Value, "").ToString()
            emailVisitante = If(selectedRow.Cells("Email").Value, "").ToString()
            Dim dataValor As Object = selectedRow.Cells("Data").Value
            Dim dataFormatada As String = ""
            If dataValor IsNot Nothing AndAlso Not IsDBNull(dataValor) Then
                dataFormatada = Convert.ToDateTime(dataValor).ToString("dd/MM/yyyy")
            End If
            Dim responsavel As String = If(selectedRow.Cells("Responsavel").Value, "").ToString()
            Dim observacao As String = If(selectedRow.Cells("Observacao").Value, "").ToString()
            Dim preConfirmado As String = If(selectedRow.Cells("PreConfirmado").Value, "").ToString()
            Dim almoco As String = If(selectedRow.Cells("Almoco").Value, "Não").ToString()
            Dim PrintDoc As New PrintDocument()
            AddHandler PrintDoc.PrintPage,
                Sub(sender, e)
                    Dim fonteNegrito As New Font("Arial", 14, FontStyle.Bold)
                    Dim fonteNormal As New Font("Arial", 10)
                    Dim fonteObs As New Font("Arial", 9, FontStyle.Italic)
                    Dim brush As New SolidBrush(Color.Black)
                    Dim margemSuperior As Integer = 0
                    Dim margemEsquerda As Integer = 5
                    Dim centroX As Integer = 70
                    Dim centroY As Integer = 105
                    e.Graphics.TranslateTransform(centroX, centroY)
                    e.Graphics.RotateTransform(90)
                    e.Graphics.TranslateTransform(-centroX, -centroY)
                    e.Graphics.DrawString("Visitante", fonteNegrito, brush, margemEsquerda, margemSuperior)
                    e.Graphics.DrawString("Nome: " & nomeVisitante, fonteNormal, brush, margemEsquerda, margemSuperior + 24)
                    e.Graphics.DrawString("Empresa: " & empresaVisitante, fonteNormal, brush, margemEsquerda, margemSuperior + 50)
                    e.Graphics.DrawString("Telefone: +" & telefoneVisitante, fonteNormal, brush, margemEsquerda, margemSuperior + 80)
                    e.Graphics.DrawString("Email: " & emailVisitante, fonteNormal, brush, margemEsquerda, margemSuperior + 110)
                    e.Graphics.DrawString("Data: " & dataFormatada, fonteNormal, brush, margemEsquerda, margemSuperior + 140)
                    e.Graphics.DrawString("Responsável: " & responsavel, fonteNormal, brush, margemEsquerda, margemSuperior + 170)
                    e.Graphics.DrawString("Observação: " & observacao, fonteObs, brush, margemEsquerda, margemSuperior + 200)
                    e.Graphics.DrawString("Pré-Confirmado: " & preConfirmado, fonteNormal, brush, margemEsquerda, margemSuperior + 230)
                    e.Graphics.DrawString("Almoço: " & almoco, fonteNormal, brush, margemEsquerda, margemSuperior + 260)
                    Dim logoPath As String = Path.Combine(Application.StartupPath, "Imagens", "logo-virt.jpeg")
                    If File.Exists(logoPath) Then
                        Dim larguraImagem As Integer = 30
                        Dim alturaImagem As Integer = 120
                        Using logo As Image = Image.FromFile(logoPath)
                            e.Graphics.DrawImage(logo, margemEsquerda - 40, margemSuperior + 30, larguraImagem, alturaImagem)
                        End Using
                    End If
                    e.Graphics.ResetTransform()
                End Sub
            Dim printDialog As New PrintDialog()
            printDialog.Document = PrintDoc
            If printDialog.ShowDialog() = DialogResult.OK Then
                PrintDoc.Print()
            End If
        Else
            MessageBox.Show("Selecione um visitante para imprimir.", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Warning)
        End If
    End Sub

    Private Sub ExportarExcelToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ExportarExcelToolStripMenuItem.Click
        ExportarParaExcel()
    End Sub

    Private Sub ExportarParaExcel()
        Try
            Dim appExcel As New Excel.Application
            Dim workbook As Excel.Workbook = appExcel.Workbooks.Add()
            Dim worksheet As Excel.Worksheet = CType(workbook.Sheets(1), Excel.Worksheet)
            For i As Integer = 1 To dgvVisitantes.Columns.Count
                worksheet.Cells(1, i) = dgvVisitantes.Columns(i - 1).HeaderText
            Next
            For i As Integer = 0 To dgvVisitantes.Rows.Count - 1
                For j As Integer = 0 To dgvVisitantes.Columns.Count - 1
                    If dgvVisitantes.Rows(i).Cells(j).Value IsNot Nothing Then
                        worksheet.Cells(i + 2, j + 1) = dgvVisitantes.Rows(i).Cells(j).Value.ToString()
                    Else
                        worksheet.Cells(i + 2, j + 1) = ""
                    End If
                Next
            Next
            Dim saveFileDialog As New SaveFileDialog()
            saveFileDialog.Filter = "Arquivos Excel (*.xlsx)|*.xlsx"
            saveFileDialog.Title = "Salvar arquivo Excel"
            saveFileDialog.FileName = "Visitantes.xlsx"
            Dim resultado As DialogResult = saveFileDialog.ShowDialog()
            If resultado = DialogResult.OK Then
                Dim caminho As String = saveFileDialog.FileName
                workbook.SaveAs(caminho)
            Else
                workbook.Close(False)
                appExcel.Quit()
                ReleaseComObject(worksheet)
                ReleaseComObject(workbook)
                ReleaseComObject(appExcel)
                Return
            End If
            workbook.Close()
            appExcel.Quit()
            ReleaseComObject(worksheet)
            ReleaseComObject(workbook)
            ReleaseComObject(appExcel)
            MessageBox.Show("Exportação concluída com sucesso!", "Sucesso", MessageBoxButtons.OK, MessageBoxIcon.Information)
        Catch ex As Exception
            MessageBox.Show("Erro ao exportar para Excel: " & ex.Message, "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    Private Sub ReleaseComObject(ByVal obj As Object)
        Try
            If obj IsNot Nothing Then
                System.Runtime.InteropServices.Marshal.ReleaseComObject(obj)
                obj = Nothing
            End If
        Catch ex As Exception
            obj = Nothing
        Finally
            GC.Collect()
        End Try
    End Sub

    Private Sub ArovarOuRejeitarToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ArovarOuRejeitarToolStripMenuItem.Click
        Dim frm As New Aprovacao()
        frm.Show()
        Me.Close()
    End Sub

    Private Sub SairToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles SairToolStripMenuItem.Click
        Application.Exit()
    End Sub

    Private Sub GraficosToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles GraficosToolStripMenuItem.Click
        Dim frm As New Grafico_Empresas()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub PedidosPendentesToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles PedidosPendentesToolStripMenuItem1.Click
        Dim frm As New Grafico_Total_Visitantes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaComFotoToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaComFotoToolStripMenuItem.Click
        Dim frm As New Lista_Individual()
        frm.Show()
        Me.Close()
    End Sub

    Private Sub ClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ClientesToolStripMenuItem.Click
        Dim frm As New InserirVisitantes()
        frm.Show()
        Me.Close()
    End Sub

    Private Sub ImprimirToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ImprimirToolStripMenuItem.Click
        PrintFicha()
    End Sub

    Private Sub MenuToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles MenuToolStripMenuItem.Click

    End Sub

    Private Sub MenuToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles MenuToolStripMenuItem1.Click
        Dim frm As New Menu()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ClientesToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles ClientesToolStripMenuItem1.Click
        Dim frm As New InserirVisitantesFornecedores()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaDeClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeClientesToolStripMenuItem.Click
        Dim frm As New ListaClientes()
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

    Private Sub InserirClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles InserirClientesToolStripMenuItem.Click
        Dim frm As New Clientes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaDeVisitantesClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeVisitantesClientesToolStripMenuItem.Click
        Dim frm As New ListaVisitantes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaDeVisitantesFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeVisitantesFornecedoresToolStripMenuItem.Click
        Dim frm As New ListaVisitantesFornecedores()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub VisitantesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles VisitantesToolStripMenuItem.Click

    End Sub
End Class
