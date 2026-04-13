Imports System.Data.SqlClient
Imports System.Text.RegularExpressions
Imports System.Threading.Tasks
Imports Microsoft.Data.SqlClient

Public Class ListaFornecedores

    '----------------- Controles de UI dinâmicos -----------------

    Private lblCabecalho As Label
    Private panelFiltro As Panel
    Private txtFiltro As TextBox

    ' Paginação
    Private paginaAtual As Integer = 1
    Private totalRegistros As Integer = 0
    Private registrosPorPagina As Integer = 20
    Private filtroNomeEmpresa As String = ""
    Private filtroTimer As Timer

    Private WithEvents btnPrimeiro As Button
    Private WithEvents btnAnterior As Button
    Private WithEvents btnProximo As Button
    Private WithEvents btnUltimo As Button
    Private lblPagina As Label

    ' Ligação SQL
    Private ReadOnly connString As String =
        "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"

    '====================== LOAD / LAYOUT ======================

    Private Async Sub ListaFornecedores_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        InicializarCabecalho()
        InicializarFiltro()
        InicializarColunasAcoes()
        InicializarControlesPaginacao()
        ConfigurarGrid()
        ReposicionarControles()

        totalRegistros = Await ObterTotalRegistrosAsync(filtroNomeEmpresa)
        Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
        AtualizarLabelPagina()
        AtualizarEstadoBotoes()
    End Sub

    Private Sub InicializarCabecalho()
        If lblCabecalho IsNot Nothing Then Return

        lblCabecalho = New Label()
        lblCabecalho.Text = "LISTA DE FORNECEDORES"
        lblCabecalho.Font = New Font("Segoe UI", 14, FontStyle.Bold)
        lblCabecalho.TextAlign = ContentAlignment.MiddleCenter
        lblCabecalho.BackColor = Color.LightSkyBlue
        lblCabecalho.ForeColor = Color.Black
        lblCabecalho.BorderStyle = BorderStyle.FixedSingle
        Me.Controls.Add(lblCabecalho)
    End Sub

    Private Sub InicializarFiltro()
        If panelFiltro IsNot Nothing Then Return

        panelFiltro = New Panel()
        panelFiltro.BackColor = SystemColors.Control
        panelFiltro.BorderStyle = BorderStyle.FixedSingle

        txtFiltro = New TextBox()
        txtFiltro.Width = 250
        txtFiltro.TextAlign = HorizontalAlignment.Left
        txtFiltro.PlaceholderText = "Pesquisar por nome ou empresa..."
        AddHandler txtFiltro.TextChanged, AddressOf IniciarFiltroComDelay

        panelFiltro.Controls.Add(txtFiltro)
        Me.Controls.Add(panelFiltro)
    End Sub

    Private Sub InicializarColunasAcoes()
        If Not dgvFornecedores.Columns.Contains("Editar") Then
            Dim btnEditar As New DataGridViewButtonColumn()
            btnEditar.Name = "Editar"
            btnEditar.HeaderText = ""
            btnEditar.Text = "Editar"
            btnEditar.UseColumnTextForButtonValue = True
            dgvFornecedores.Columns.Add(btnEditar)
        End If

        If Not dgvFornecedores.Columns.Contains("Eliminar") Then
            Dim btnEliminar As New DataGridViewButtonColumn()
            btnEliminar.Name = "Eliminar"
            btnEliminar.HeaderText = ""
            btnEliminar.Text = "Eliminar"
            btnEliminar.UseColumnTextForButtonValue = True
            dgvFornecedores.Columns.Add(btnEliminar)
        End If
    End Sub

    Private Sub InicializarControlesPaginacao()
        If btnPrimeiro Is Nothing Then
            btnPrimeiro = New Button()
            btnPrimeiro.Text = "Primeiro"
            btnPrimeiro.Size = New Size(75, 25)
            AddHandler btnPrimeiro.Click, AddressOf btnPrimeiro_Click
            Me.Controls.Add(btnPrimeiro)
        End If

        If btnAnterior Is Nothing Then
            btnAnterior = New Button()
            btnAnterior.Text = "Anterior"
            btnAnterior.Size = New Size(75, 25)
            AddHandler btnAnterior.Click, AddressOf btnAnterior_Click
            Me.Controls.Add(btnAnterior)
        End If

        If btnProximo Is Nothing Then
            btnProximo = New Button()
            btnProximo.Text = "Próximo"
            btnProximo.Size = New Size(75, 25)
            AddHandler btnProximo.Click, AddressOf btnProximo_Click
            Me.Controls.Add(btnProximo)
        End If

        If btnUltimo Is Nothing Then
            btnUltimo = New Button()
            btnUltimo.Text = "Último"
            btnUltimo.Size = New Size(75, 25)
            AddHandler btnUltimo.Click, AddressOf btnUltimo_Click
            Me.Controls.Add(btnUltimo)
        End If

        If lblPagina Is Nothing Then
            lblPagina = New Label()
            lblPagina.Size = New Size(180, 25)
            lblPagina.TextAlign = ContentAlignment.MiddleLeft
            Me.Controls.Add(lblPagina)
        End If
    End Sub

    Private Sub ConfigurarGrid()
        dgvFornecedores.Anchor = AnchorStyles.Top Or AnchorStyles.Left Or AnchorStyles.Right Or AnchorStyles.Bottom
        dgvFornecedores.ColumnHeadersHeight = 48
        dgvFornecedores.ColumnHeadersDefaultCellStyle.Font = New Font("Segoe UI", 12, FontStyle.Bold)
        dgvFornecedores.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
        AddHandler dgvFornecedores.CellContentClick, AddressOf dgvFornecedores_CellContentClick
    End Sub

    Private Sub ReposicionarControles()
        ' Proteção contra chamadas antes dos controlos existirem
        If lblCabecalho Is Nothing OrElse panelFiltro Is Nothing _
           OrElse btnPrimeiro Is Nothing OrElse btnAnterior Is Nothing _
           OrElse btnProximo Is Nothing OrElse btnUltimo Is Nothing _
           OrElse dgvFornecedores Is Nothing OrElse txtFiltro Is Nothing _
           OrElse lblPagina Is Nothing Then
            Exit Sub
        End If

        Dim margem As Integer = 10

        lblCabecalho.Location = New Point(margem, 25)
        lblCabecalho.Size = New Size(Me.ClientSize.Width - 2 * margem, 38)

        panelFiltro.Location = New Point(margem, lblCabecalho.Bottom + 10)
        panelFiltro.Size = New Size(Me.ClientSize.Width - 2 * margem, 36)
        txtFiltro.Location = New Point(10, 6)

        Dim yPag As Integer = panelFiltro.Bottom + 10
        btnPrimeiro.Location = New Point(margem, yPag)
        btnAnterior.Location = New Point(margem + 90, yPag)
        btnProximo.Location = New Point(margem + 180, yPag)
        btnUltimo.Location = New Point(margem + 270, yPag)
        lblPagina.Location = New Point(margem + 360, yPag + 4)

        dgvFornecedores.Location = New Point(margem, btnPrimeiro.Bottom + 10)
        dgvFornecedores.Size = New Size(Me.ClientSize.Width - 2 * margem,
                                        Me.ClientSize.Height - dgvFornecedores.Top - margem)
    End Sub

    Private Sub ListaFornecedores_Resize(sender As Object, e As EventArgs) Handles MyBase.Resize
        ReposicionarControles()
    End Sub

    '====================== PAGINAÇÃO / FILTRO ======================

    Private Async Sub IniciarFiltroComDelay(sender As Object, e As EventArgs)
        If filtroTimer IsNot Nothing Then
            filtroTimer.Stop()
            RemoveHandler filtroTimer.Tick, AddressOf ExecutarFiltro
        End If

        filtroTimer = New Timer()
        filtroTimer.Interval = 500
        AddHandler filtroTimer.Tick, AddressOf ExecutarFiltro
        filtroTimer.Start()
    End Sub

    Private Async Sub ExecutarFiltro(sender As Object, e As EventArgs)
        filtroTimer.Stop()
        RemoveHandler filtroTimer.Tick, AddressOf ExecutarFiltro
        filtroTimer = Nothing

        filtroNomeEmpresa = txtFiltro.Text.Trim()
        paginaAtual = 1
        totalRegistros = Await ObterTotalRegistrosAsync(filtroNomeEmpresa)
        Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
        AtualizarLabelPagina()
        AtualizarEstadoBotoes()
    End Sub

    Private Async Function ObterTotalRegistrosAsync(Optional filtro As String = "") As Task(Of Integer)
        Dim total As Integer = 0
        Dim query As String =
            "SELECT COUNT(*) FROM Fornecedores " &
            "WHERE Nome LIKE @Filtro OR Empresa LIKE @Filtro"

        Try
            Using conn As New SqlConnection(connString)
                Using cmd As New SqlCommand(query, conn)
                    cmd.Parameters.AddWithValue("@Filtro", "%" & filtro & "%")
                    Await conn.OpenAsync()
                    total = Convert.ToInt32(Await cmd.ExecuteScalarAsync())
                End Using
            End Using
        Catch ex As Exception
            MessageBox.Show("Erro ao obter total de registos: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try

        Return total
    End Function

    Private Async Function CarregarDadosPaginaAsync(pagina As Integer,
                                                    Optional filtro As String = "") As Task
        Dim offset As Integer = (pagina - 1) * registrosPorPagina
        Dim query As String =
            "SELECT Id, Nome, Empresa, Telefone, Email " &
            "FROM Fornecedores " &
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
                    adapter.Fill(tabela)

                    dgvFornecedores.DataSource = tabela
                End Using
            End Using

            ConfigurarColunasGrid()

        Catch ex As Exception
            MessageBox.Show("Erro ao carregar os dados: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Function

    Private Sub ConfigurarColunasGrid()
        If dgvFornecedores.Columns.Contains("Id") Then
            dgvFornecedores.Columns("Id").Visible = False
        End If
        If dgvFornecedores.Columns.Contains("Nome") Then
            With dgvFornecedores.Columns("Nome")
                .HeaderText = "Nome"
                .DisplayIndex = 0
            End With
        End If
        If dgvFornecedores.Columns.Contains("Empresa") Then
            With dgvFornecedores.Columns("Empresa")
                .HeaderText = "Empresa"
                .DisplayIndex = 1
            End With
        End If
        If dgvFornecedores.Columns.Contains("Telefone") Then
            With dgvFornecedores.Columns("Telefone")
                .HeaderText = "Telefone"
                .DisplayIndex = 2
            End With
        End If
        If dgvFornecedores.Columns.Contains("Email") Then
            With dgvFornecedores.Columns("Email")
                .HeaderText = "Email"
                .DisplayIndex = 3
            End With
        End If

        Dim totalCols As Integer = dgvFornecedores.Columns.Count
        If dgvFornecedores.Columns.Contains("Editar") Then
            dgvFornecedores.Columns("Editar").DisplayIndex = totalCols - 2
        End If
        If dgvFornecedores.Columns.Contains("Eliminar") Then
            dgvFornecedores.Columns("Eliminar").DisplayIndex = totalCols - 1
        End If
    End Sub

    Private Sub AtualizarLabelPagina()
        Dim totalPaginas As Integer = 0
        If totalRegistros > 0 Then
            totalPaginas = CInt(Math.Ceiling(totalRegistros / CDbl(registrosPorPagina)))
        End If
        lblPagina.Text = "Página " & paginaAtual.ToString() &
                         " de " & totalPaginas.ToString()
    End Sub

    Private Sub AtualizarEstadoBotoes()
        Dim totalPaginas As Integer = 0
        If totalRegistros > 0 Then
            totalPaginas = CInt(Math.Ceiling(totalRegistros / CDbl(registrosPorPagina)))
        End If

        btnPrimeiro.Enabled = (paginaAtual > 1)
        btnAnterior.Enabled = (paginaAtual > 1)
        btnProximo.Enabled = (paginaAtual < totalPaginas)
        btnUltimo.Enabled = (paginaAtual < totalPaginas)
    End Sub

    Private Async Sub btnPrimeiro_Click(sender As Object, e As EventArgs)
        If paginaAtual = 1 Then Return
        paginaAtual = 1
        Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
        AtualizarLabelPagina()
        AtualizarEstadoBotoes()
    End Sub

    Private Async Sub btnAnterior_Click(sender As Object, e As EventArgs)
        If paginaAtual <= 1 Then Return
        paginaAtual -= 1
        Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
        AtualizarLabelPagina()
        AtualizarEstadoBotoes()
    End Sub

    Private Async Sub btnProximo_Click(sender As Object, e As EventArgs)
        Dim totalPaginas As Integer = CInt(Math.Ceiling(totalRegistros / CDbl(registrosPorPagina)))
        If paginaAtual >= totalPaginas Then Return
        paginaAtual += 1
        Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
        AtualizarLabelPagina()
        AtualizarEstadoBotoes()
    End Sub

    Private Async Sub btnUltimo_Click(sender As Object, e As EventArgs)
        Dim totalPaginas As Integer = CInt(Math.Ceiling(totalRegistros / CDbl(registrosPorPagina)))
        If paginaAtual = totalPaginas Then Return
        paginaAtual = totalPaginas
        Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
        AtualizarLabelPagina()
        AtualizarEstadoBotoes()
    End Sub

    '====================== GRID: EDITAR / ELIMINAR ======================

    Private Sub dgvFornecedores_CellContentClick(sender As Object, e As DataGridViewCellEventArgs)
        If e.RowIndex < 0 Then Return
        Dim coluna As String = dgvFornecedores.Columns(e.ColumnIndex).Name

        If coluna = "Editar" Then
            EditarFornecedorAsync(e.RowIndex)
        ElseIf coluna = "Eliminar" Then
            EliminarFornecedorAsync(e.RowIndex)
        End If
    End Sub

    Private Async Sub EditarFornecedorAsync(rowIndex As Integer)
        Dim tabela As DataTable = TryCast(dgvFornecedores.DataSource, DataTable)
        If tabela Is Nothing Then Return

        Dim rowView As DataRowView =
            CType(dgvFornecedores.Rows(rowIndex).DataBoundItem, DataRowView)
        Dim linha As DataRow = rowView.Row

        Using frmEdicao As New Form()
            frmEdicao.Text = "Editar Fornecedor"
            frmEdicao.Size = New Size(400, 260)
            frmEdicao.FormBorderStyle = FormBorderStyle.FixedDialog
            frmEdicao.MaximizeBox = False
            frmEdicao.MinimizeBox = False
            frmEdicao.StartPosition = FormStartPosition.CenterParent

            Dim txtNome As New TextBox()
            txtNome.Left = 130
            txtNome.Top = 20
            txtNome.Width = 200
            txtNome.Text = linha("Nome").ToString()

            Dim txtEmpresa As New TextBox()
            txtEmpresa.Left = 130
            txtEmpresa.Top = 60
            txtEmpresa.Width = 200
            txtEmpresa.Text = linha("Empresa").ToString()

            Dim txtTelefone As New TextBox()
            txtTelefone.Left = 130
            txtTelefone.Top = 100
            txtTelefone.Width = 200
            txtTelefone.Text = linha("Telefone").ToString()

            Dim txtEmail As New TextBox()
            txtEmail.Left = 130
            txtEmail.Top = 140
            txtEmail.Width = 200
            txtEmail.Text = linha("Email").ToString()

            frmEdicao.Controls.AddRange(New Control() {
                New Label() With {.Text = "Nome:", .Left = 20, .Top = 20, .Width = 100},
                txtNome,
                New Label() With {.Text = "Empresa:", .Left = 20, .Top = 60, .Width = 100},
                txtEmpresa,
                New Label() With {.Text = "Telefone:", .Left = 20, .Top = 100, .Width = 100},
                txtTelefone,
                New Label() With {.Text = "Email:", .Left = 20, .Top = 140, .Width = 100},
                txtEmail
            })

            Dim btnGravar As New Button()
            btnGravar.Text = "Gravar"
            btnGravar.Left = 130
            btnGravar.Top = 190
            btnGravar.Width = 100

            AddHandler btnGravar.Click,
                Async Sub()
                    Dim nome As String = txtNome.Text.Trim()
                    Dim empresa As String = txtEmpresa.Text.Trim()
                    Dim telefone As String = txtTelefone.Text.Trim()
                    Dim email As String = txtEmail.Text.Trim()

                    If String.IsNullOrWhiteSpace(nome) OrElse
                       String.IsNullOrWhiteSpace(empresa) OrElse
                       String.IsNullOrWhiteSpace(telefone) OrElse
                       String.IsNullOrWhiteSpace(email) Then

                        MessageBox.Show("Por favor, preencha todos os campos.",
                                        "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                        Exit Sub
                    End If

                    If Not Regex.IsMatch(telefone, "^[\d\s]+$") Then
                        MessageBox.Show("O telefone deve conter apenas números e espaços.",
                                        "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                        Exit Sub
                    End If

                    Dim padraoEmail As String = "^[^@\s]+@[^@\s]+\.[^@\s]+$"
                    If Not Regex.IsMatch(email, padraoEmail) Then
                        MessageBox.Show("O email introduzido não é válido.",
                                        "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                        Exit Sub
                    End If

                    Dim idFornecedor As Integer = CInt(linha("Id"))

                    Try
                        Using conn As New SqlConnection(connString)
                            Using cmd As New SqlCommand("
UPDATE Fornecedores
   SET Nome=@Nome,
       Empresa=@Empresa,
       Telefone=@Telefone,
       Email=@Email
 WHERE Id=@Id", conn)

                                cmd.Parameters.AddWithValue("@Nome", nome)
                                cmd.Parameters.AddWithValue("@Empresa", empresa)
                                cmd.Parameters.AddWithValue("@Telefone", telefone)
                                cmd.Parameters.AddWithValue("@Email", email)
                                cmd.Parameters.AddWithValue("@Id", idFornecedor)

                                Await conn.OpenAsync()
                                Await cmd.ExecuteNonQueryAsync()
                            End Using
                        End Using

                        frmEdicao.DialogResult = DialogResult.OK

                    Catch ex As Exception
                        MessageBox.Show("Erro ao gravar alterações: " & ex.Message,
                                        "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                    End Try
                End Sub

            frmEdicao.Controls.Add(btnGravar)

            If frmEdicao.ShowDialog() = DialogResult.OK Then
                Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
                AtualizarLabelPagina()
            End If
        End Using
    End Sub

    Private Async Sub EliminarFornecedorAsync(rowIndex As Integer)
        Dim tabela As DataTable = TryCast(dgvFornecedores.DataSource, DataTable)
        If tabela Is Nothing Then Return

        Dim rowView As DataRowView =
            CType(dgvFornecedores.Rows(rowIndex).DataBoundItem, DataRowView)
        Dim linha As DataRow = rowView.Row
        Dim idFornecedor As Integer = CInt(linha("Id"))

        Dim confirmResult As DialogResult =
            MessageBox.Show("Confirmar eliminação do Fornecedor?",
                            "Atenção", MessageBoxButtons.YesNo,
                            MessageBoxIcon.Warning)

        If confirmResult <> DialogResult.Yes Then Return

        Try
            Using conn As New SqlConnection(connString)
                Using cmd As New SqlCommand("DELETE FROM Fornecedores WHERE Id = @Id", conn)
                    cmd.Parameters.AddWithValue("@Id", idFornecedor)
                    Await conn.OpenAsync()
                    Await cmd.ExecuteNonQueryAsync()
                End Using
            End Using

            MessageBox.Show("Fornecedor eliminado com sucesso.",
                            "Informação", MessageBoxButtons.OK, MessageBoxIcon.Information)

            totalRegistros = Await ObterTotalRegistrosAsync(filtroNomeEmpresa)
            Dim totalPaginas As Integer =
                CInt(Math.Ceiling(totalRegistros / CDbl(registrosPorPagina)))
            If paginaAtual > totalPaginas AndAlso paginaAtual > 1 Then
                paginaAtual -= 1
            End If
            Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
            AtualizarLabelPagina()
            AtualizarEstadoBotoes()

        Catch ex As Exception
            MessageBox.Show("Erro ao eliminar Fornecedor: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    '====================== MENUS / NAVEGAÇÃO ======================

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

    Private Sub ClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ClientesToolStripMenuItem.Click

    End Sub

    Private Sub ListaDeFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeFornecedoresToolStripMenuItem.Click
        Dim frm As New ListaFornecedores()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub FornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles FornecedoresToolStripMenuItem.Click

    End Sub

    Private Sub InserirFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles InserirFornecedoresToolStripMenuItem.Click
        Dim frm As New Fornecedores()
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

    Private Sub ListaDeVisitantesFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeVisitantesFornecedoresToolStripMenuItem.Click
        Dim frm As New ListaVisitantesFornecedores()
        frm.Show()
        Me.Hide()
    End Sub
End Class
