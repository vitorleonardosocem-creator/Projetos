Imports System.Data.SqlClient
Imports System.Threading.Tasks
Imports System.Text.RegularExpressions
Imports Microsoft.Data.SqlClient

Public Class ListaClientes

    Private lblCabecalho As Label
    Private panelFiltro As Panel

    ' paginação
    Private paginaAtual As Integer = 1
    Private totalRegistros As Integer = 0
    Private registrosPorPagina As Integer = 20
    Private filtroNomeEmpresa As String = ""

    Private WithEvents btnPrimeiro As Button
    Private WithEvents btnAnterior As Button
    Private WithEvents btnProximo As Button
    Private WithEvents btnUltimo As Button
    Private lblPagina As Label

    Private ReadOnly connString As String =
        "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"

    Private Async Sub ListaClientes_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        AdicionarCabecalho()
        AdicionarFiltroNoDataGridView()
        InicializarColunasAcoes()
        InicializarControlesPaginacao()

        dgvClientes.Location = New Point(10, panelFiltro.Bottom + 50)
        dgvClientes.Size = New Size(Me.ClientSize.Width - 20, Me.ClientSize.Height - panelFiltro.Bottom - 60)
        dgvClientes.Anchor = AnchorStyles.Top Or AnchorStyles.Left Or AnchorStyles.Right Or AnchorStyles.Bottom
        dgvClientes.ColumnHeadersHeight = 48
        dgvClientes.ColumnHeadersDefaultCellStyle.Font = New Font("Segoe UI", 12, FontStyle.Bold)
        AddHandler dgvClientes.CellContentClick, AddressOf dgvClientes_CellContentClick

        totalRegistros = Await ObterTotalRegistrosAsync(filtroNomeEmpresa)
        Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
        AtualizarLabelPagina()
    End Sub

    Private Sub AdicionarCabecalho()
        If lblCabecalho Is Nothing Then
            lblCabecalho = New Label()
            lblCabecalho.Text = "LISTA DE CLIENTES"
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
        If dgvClientes.Columns.Contains("Editar") = False Then
            Dim btnEditar As New DataGridViewButtonColumn()
            btnEditar.Name = "Editar"
            btnEditar.HeaderText = ""
            btnEditar.Text = "Editar"
            btnEditar.UseColumnTextForButtonValue = True
            dgvClientes.Columns.Add(btnEditar)
        End If

        If dgvClientes.Columns.Contains("Eliminar") = False Then
            Dim btnEliminar As New DataGridViewButtonColumn()
            btnEliminar.Name = "Eliminar"
            btnEliminar.HeaderText = ""
            btnEliminar.Text = "Eliminar"
            btnEliminar.UseColumnTextForButtonValue = True
            dgvClientes.Columns.Add(btnEliminar)
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
        Dim query As String =
            "SELECT COUNT(*) FROM Clientes " &
            "WHERE Nome LIKE @Filtro OR Empresa LIKE @Filtro"

        Using conn As New SqlConnection(connString)
            Using cmd As New SqlCommand(query, conn)
                cmd.Parameters.AddWithValue("@Filtro", "%" & filtro & "%")
                Await conn.OpenAsync()
                Return Convert.ToInt32(Await cmd.ExecuteScalarAsync())
            End Using
        End Using
    End Function

    Private Async Function CarregarDadosPaginaAsync(pagina As Integer, Optional filtro As String = "") As Task
        Dim offset As Integer = (pagina - 1) * registrosPorPagina
        Dim query As String =
            "SELECT IdCliente, Nome, Empresa, Telefone, Email " &
            "FROM Clientes " &
            "WHERE Nome LIKE @Filtro OR Empresa LIKE @Filtro " &
            "ORDER BY Nome ASC " &
            "OFFSET @Offset ROWS FETCH NEXT @Limite ROWS ONLY"

        Try
            Using conn As New SqlConnection(connString)
                Using cmd As New SqlCommand(query, conn)
                    cmd.Parameters.AddWithValue("@Filtro", "%" & filtro & "%")
                    cmd.Parameters.AddWithValue("@Offset", offset)
                    cmd.Parameters.AddWithValue("@Limite", registrosPorPagina)

                    Dim adapter As New SqlDataAdapter(cmd)
                    Dim tabela As New DataTable()
                    Await conn.OpenAsync()
                    Await Task.Run(Sub() adapter.Fill(tabela))
                    dgvClientes.DataSource = tabela

                    If dgvClientes.Columns.Contains("IdCliente") Then dgvClientes.Columns("IdCliente").Visible = False
                    If dgvClientes.Columns.Contains("Nome") Then dgvClientes.Columns("Nome").HeaderText = "Nome"
                    If dgvClientes.Columns.Contains("Empresa") Then dgvClientes.Columns("Empresa").HeaderText = "Empresa"
                    If dgvClientes.Columns.Contains("Telefone") Then dgvClientes.Columns("Telefone").HeaderText = "Telefone"
                    If dgvClientes.Columns.Contains("Email") Then dgvClientes.Columns("Email").HeaderText = "Email"

                    If dgvClientes.Columns.Contains("Nome") Then dgvClientes.Columns("Nome").DisplayIndex = 0
                    If dgvClientes.Columns.Contains("Empresa") Then dgvClientes.Columns("Empresa").DisplayIndex = 1
                    If dgvClientes.Columns.Contains("Telefone") Then dgvClientes.Columns("Telefone").DisplayIndex = 2
                    If dgvClientes.Columns.Contains("Email") Then dgvClientes.Columns("Email").DisplayIndex = 3

                    Dim totalCols = dgvClientes.Columns.Count
                    If dgvClientes.Columns.Contains("Editar") Then dgvClientes.Columns("Editar").DisplayIndex = totalCols - 2
                    If dgvClientes.Columns.Contains("Eliminar") Then dgvClientes.Columns("Eliminar").DisplayIndex = totalCols - 1
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

    Private Sub dgvClientes_CellContentClick(sender As Object, e As DataGridViewCellEventArgs)
        If e.RowIndex < 0 Then Return
        Dim coluna = dgvClientes.Columns(e.ColumnIndex).Name
        If coluna = "Editar" Then
            EditarClienteAsync(e.RowIndex)
        ElseIf coluna = "Eliminar" Then
            EliminarClienteAsync(e.RowIndex)
        End If
    End Sub

    Private Async Sub EditarClienteAsync(rowIndex As Integer)
        Dim tabela As DataTable = TryCast(dgvClientes.DataSource, DataTable)
        If tabela Is Nothing Then Return

        Dim rowView As DataRowView = CType(dgvClientes.Rows(rowIndex).DataBoundItem, DataRowView)
        Dim linha As DataRow = rowView.Row

        Using frmEdicao As New Form()
            frmEdicao.Text = "Editar Cliente"
            frmEdicao.Size = New Size(400, 260)
            frmEdicao.FormBorderStyle = FormBorderStyle.FixedDialog
            frmEdicao.MaximizeBox = False
            frmEdicao.MinimizeBox = False
            frmEdicao.StartPosition = FormStartPosition.CenterParent

            Dim txtNome As New TextBox() With {.Left = 130, .Top = 20, .Width = 200, .Text = linha("Nome").ToString()}
            Dim txtEmpresa As New TextBox() With {.Left = 130, .Top = 60, .Width = 200, .Text = linha("Empresa").ToString()}
            Dim txtTelefone As New TextBox() With {.Left = 130, .Top = 100, .Width = 200, .Text = linha("Telefone").ToString()}
            Dim txtEmail As New TextBox() With {.Left = 130, .Top = 140, .Width = 200, .Text = linha("Email").ToString()}

            frmEdicao.Controls.AddRange({
                New Label() With {.Text = "Nome:", .Left = 20, .Top = 20, .Width = 100},
                txtNome,
                New Label() With {.Text = "Empresa:", .Left = 20, .Top = 60, .Width = 100},
                txtEmpresa,
                New Label() With {.Text = "Telefone:", .Left = 20, .Top = 100, .Width = 100},
                txtTelefone,
                New Label() With {.Text = "Email:", .Left = 20, .Top = 140, .Width = 100},
                txtEmail
            })

            Dim btnGravar As New Button() With {.Text = "Gravar", .Left = 130, .Top = 190, .Width = 100}
            AddHandler btnGravar.Click,
                Async Sub()
                    ' Normalizar textos
                    Dim nome As String = txtNome.Text.Trim()
                    Dim empresa As String = txtEmpresa.Text.Trim()
                    Dim telefone As String = txtTelefone.Text.Trim()
                    Dim email As String = txtEmail.Text.Trim()

                    ' Validações básicas
                    If String.IsNullOrWhiteSpace(nome) OrElse
                       String.IsNullOrWhiteSpace(empresa) OrElse
                       String.IsNullOrWhiteSpace(telefone) OrElse
                       String.IsNullOrWhiteSpace(email) Then

                        MessageBox.Show("Por favor, preencha todos os campos.", "Erro",
                                        MessageBoxButtons.OK, MessageBoxIcon.Error)
                        Exit Sub
                    End If

                    ' Telefone: apenas dígitos e espaços
                    If Not Regex.IsMatch(telefone, "^[\d\s]+$") Then
                        MessageBox.Show("O telefone deve conter apenas números e espaços.", "Erro",
                                        MessageBoxButtons.OK, MessageBoxIcon.Error)
                        Exit Sub
                    End If

                    ' Email: tem de conter '@' e respeitar formato simples
                    If Not email.Contains("@") Then
                        MessageBox.Show("O email deve conter '@'.", "Erro",
                                        MessageBoxButtons.OK, MessageBoxIcon.Error)
                        Exit Sub
                    End If

                    Dim padraoEmail As String = "^[^@\s]+@[^@\s]+\.[^@\s]+$"
                    If Not Regex.IsMatch(email, padraoEmail) Then
                        MessageBox.Show("O email introduzido não é válido.", "Erro",
                                        MessageBoxButtons.OK, MessageBoxIcon.Error)
                        Exit Sub
                    End If

                    Dim idCliente As Integer = Convert.ToInt32(linha("IdCliente"))

                    Try
                        Using conn As New SqlConnection(connString)
                            Await conn.OpenAsync()
                            Dim query As String =
                                "UPDATE Clientes " &
                                "SET Nome=@Nome, Empresa=@Empresa, Telefone=@Telefone, Email=@Email " &
                                "WHERE IdCliente=@IdCliente"

                            Using cmd As New SqlCommand(query, conn)
                                cmd.Parameters.AddWithValue("@Nome", nome)
                                cmd.Parameters.AddWithValue("@Empresa", empresa)
                                cmd.Parameters.AddWithValue("@Telefone", telefone)
                                cmd.Parameters.AddWithValue("@Email", email)
                                cmd.Parameters.AddWithValue("@IdCliente", idCliente)
                                Await cmd.ExecuteNonQueryAsync()
                            End Using
                        End Using

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

    Private Async Sub EliminarClienteAsync(rowIndex As Integer)
        Dim tabela As DataTable = TryCast(dgvClientes.DataSource, DataTable)
        If tabela Is Nothing Then Return

        Dim rowView As DataRowView = CType(dgvClientes.Rows(rowIndex).DataBoundItem, DataRowView)
        Dim linha As DataRow = rowView.Row
        Dim idCliente As Integer = Convert.ToInt32(linha("IdCliente"))

        Dim confirmResult As DialogResult =
            MessageBox.Show("Confirmar eliminação do cliente?", "Atenção",
                            MessageBoxButtons.YesNo, MessageBoxIcon.Warning)

        If confirmResult = DialogResult.Yes Then
            Try
                Using conn As New SqlConnection(connString)
                    Await conn.OpenAsync()
                    Dim query As String = "DELETE FROM Clientes WHERE IdCliente = @IdCliente"
                    Using cmd As New SqlCommand(query, conn)
                        cmd.Parameters.AddWithValue("@IdCliente", idCliente)
                        Await cmd.ExecuteNonQueryAsync()
                    End Using
                End Using

                MessageBox.Show("Cliente eliminado com sucesso.")
                totalRegistros = Await ObterTotalRegistrosAsync(filtroNomeEmpresa)
                Dim totalPaginas As Integer = Math.Ceiling(totalRegistros / registrosPorPagina)
                If paginaAtual > totalPaginas AndAlso paginaAtual > 1 Then paginaAtual -= 1
                Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
                AtualizarLabelPagina()

            Catch ex As Exception
                MessageBox.Show("Erro ao eliminar cliente: " & ex.Message)
            End Try
        End If
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

    Private Sub ClientesToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles ClientesToolStripMenuItem1.Click
        Dim frm As New InserirVisitantesFornecedores()
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

    Private Sub ListaDeClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeClientesToolStripMenuItem.Click
        Dim frm As New ListaClientes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub VisitantesToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles VisitantesToolStripMenuItem1.Click
        Dim frm As New ListaVisitantesFornecedores()
        frm.Show()
        Me.Hide()
    End Sub
End Class
