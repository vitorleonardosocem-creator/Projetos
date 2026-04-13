Imports System.Data.SqlClient
Imports System.Drawing.Printing
Imports System.IO
Imports System.Net.Mail
Imports System.Threading.Tasks
Imports Microsoft.Data.SqlClient
Imports Excel = Microsoft.Office.Interop.Excel

Public Class ListaVisitantesFornecedores

    '====================== CONFIG / VARIÁVEIS ======================

    Private ReadOnly connectionString As String =
        "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"

    ' Dados do visitante para impressão
    Private nomeVisitante As String
    Private empresaVisitante As String
    Private telefoneVisitante As String
    Private emailVisitante As String
    Private dataVisitante As String
    Private responsavelVisitante As String
    Private observacaoVisitante As String
    Private preConfirmadoVisitante As String

    ' Cabeçalho e filtro
    Private lblCabecalho As Label
    Private panelFiltro As Panel
    Private txtFiltro As TextBox
    Private filtroTimer As Timer

    ' Paginação
    Private paginaAtual As Integer = 1
    Private totalRegistros As Integer = 0
    Private registrosPorPagina As Integer = 20
    Private filtroNomeEmpresa As String = ""

    ' Controles de paginação
    Private WithEvents btnPrimeiro As Button
    Private WithEvents btnAnterior As Button
    Private WithEvents btnProximo As Button
    Private WithEvents btnUltimo As Button
    Private lblPagina As Label

    '====================== LOAD / LAYOUT ======================

    Private Async Sub ListaVisitantesFornecedores_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        InicializarControles()
        ConfigurarDataGridView()
        Await CarregarDadosIniciais()
    End Sub

    Private Sub InicializarControles()
        If lblCabecalho Is Nothing Then CriarCabecalho()
        If panelFiltro Is Nothing Then CriarFiltro()
        If btnPrimeiro Is Nothing Then CriarPaginacao()
        If lblPagina Is Nothing Then CriarLabelPagina()
        ReposicionarControles()
    End Sub

    Private Sub CriarCabecalho()
        lblCabecalho = New Label()
        lblCabecalho.Text = "LISTA DE VISITAS DE FORNECEDORES"
        lblCabecalho.Font = New Font("Segoe UI", 14, FontStyle.Bold)
        lblCabecalho.TextAlign = ContentAlignment.MiddleCenter
        lblCabecalho.BackColor = Color.LightSkyBlue
        lblCabecalho.ForeColor = Color.Black
        lblCabecalho.BorderStyle = BorderStyle.FixedSingle
        Me.Controls.Add(lblCabecalho)
    End Sub

    Private Sub CriarFiltro()
        panelFiltro = New Panel()
        panelFiltro.BackColor = SystemColors.Control
        panelFiltro.BorderStyle = BorderStyle.FixedSingle

        txtFiltro = New TextBox()
        txtFiltro.Width = 300
        txtFiltro.TextAlign = HorizontalAlignment.Left
        txtFiltro.PlaceholderText = "Pesquisar por nome ou empresa..."
        AddHandler txtFiltro.TextChanged, AddressOf IniciarFiltroComDelay

        panelFiltro.Controls.Add(txtFiltro)
        Me.Controls.Add(panelFiltro)
    End Sub

    Private Sub CriarPaginacao()
        btnPrimeiro = New Button()
        btnPrimeiro.Text = "Primeiro"
        btnPrimeiro.Size = New Size(75, 28)
        AddHandler btnPrimeiro.Click, AddressOf btnPrimeiro_Click
        Me.Controls.Add(btnPrimeiro)

        btnAnterior = New Button()
        btnAnterior.Text = "Anterior"
        btnAnterior.Size = New Size(75, 28)
        AddHandler btnAnterior.Click, AddressOf btnAnterior_Click
        Me.Controls.Add(btnAnterior)

        btnProximo = New Button()
        btnProximo.Text = "Próximo"
        btnProximo.Size = New Size(75, 28)
        AddHandler btnProximo.Click, AddressOf btnProximo_Click
        Me.Controls.Add(btnProximo)

        btnUltimo = New Button()
        btnUltimo.Text = "Último"
        btnUltimo.Size = New Size(75, 28)
        AddHandler btnUltimo.Click, AddressOf btnUltimo_Click
        Me.Controls.Add(btnUltimo)
    End Sub

    Private Sub CriarLabelPagina()
        lblPagina = New Label()
        lblPagina.Size = New Size(220, 28)
        lblPagina.TextAlign = ContentAlignment.MiddleLeft
        Me.Controls.Add(lblPagina)
    End Sub

    Private Sub ReposicionarControles()
        If lblCabecalho Is Nothing OrElse panelFiltro Is Nothing _
           OrElse txtFiltro Is Nothing OrElse btnPrimeiro Is Nothing _
           OrElse btnAnterior Is Nothing OrElse btnProximo Is Nothing _
           OrElse btnUltimo Is Nothing OrElse lblPagina Is Nothing _
           OrElse dgvVisitantes Is Nothing Then
            Exit Sub
        End If

        Dim margem As Integer = 10

        lblCabecalho.Location = New Point(margem, margem)
        lblCabecalho.Size = New Size(Me.ClientSize.Width - 2 * margem, 38)

        panelFiltro.Location = New Point(margem, lblCabecalho.Bottom + margem)
        panelFiltro.Size = New Size(Me.ClientSize.Width - 2 * margem, 36)

        txtFiltro.Location = New Point(10, 6)

        Dim yPag As Integer = panelFiltro.Bottom + 5
        btnPrimeiro.Location = New Point(margem, yPag)
        btnAnterior.Location = New Point(margem + 85, yPag)
        btnProximo.Location = New Point(margem + 170, yPag)
        btnUltimo.Location = New Point(margem + 255, yPag)
        lblPagina.Location = New Point(margem + 340, yPag + 4)

        dgvVisitantes.Location = New Point(margem, btnPrimeiro.Bottom + 5)
        dgvVisitantes.Size = New Size(Me.ClientSize.Width - 2 * margem,
                                      Me.ClientSize.Height - dgvVisitantes.Top - margem)
    End Sub

    Private Sub ListaVisitantesFornecedores_Resize(sender As Object, e As EventArgs) Handles MyBase.Resize
        ReposicionarControles()
    End Sub

    Private Sub ConfigurarDataGridView()
        dgvVisitantes.Anchor = AnchorStyles.Top Or AnchorStyles.Left Or AnchorStyles.Right Or AnchorStyles.Bottom
        dgvVisitantes.ColumnHeadersHeight = 48
        dgvVisitantes.ColumnHeadersDefaultCellStyle.Font = New Font("Segoe UI", 12, FontStyle.Bold)
        dgvVisitantes.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
        AddHandler dgvVisitantes.CellContentClick, AddressOf dgvVisitantes_CellContentClick
        InicializarColunasAcoes()
    End Sub

    '====================== PAGINAÇÃO / FILTRO ======================

    Private Async Function CarregarDadosIniciais() As Task
        totalRegistros = Await ObterTotalRegistrosAsync(filtroNomeEmpresa)
        Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
        AtualizarLabelPagina()
        AtualizarEstadoBotoes()
    End Function

    Private Sub InicializarColunasAcoes()
        If Not dgvVisitantes.Columns.Contains("Editar") Then
            Dim col As New DataGridViewButtonColumn()
            col.Name = "Editar"
            col.HeaderText = ""
            col.Text = "Editar"
            col.UseColumnTextForButtonValue = True
            dgvVisitantes.Columns.Add(col)
        End If

        If Not dgvVisitantes.Columns.Contains("Duplicar") Then
            Dim col As New DataGridViewButtonColumn()
            col.Name = "Duplicar"
            col.HeaderText = ""
            col.Text = "Duplicar"
            col.UseColumnTextForButtonValue = True
            col.Visible = False
            dgvVisitantes.Columns.Add(col)
        End If

        If Not dgvVisitantes.Columns.Contains("Eliminar") Then
            Dim col As New DataGridViewButtonColumn()
            col.Name = "Eliminar"
            col.HeaderText = ""
            col.Text = "Eliminar"
            col.UseColumnTextForButtonValue = True
            dgvVisitantes.Columns.Add(col)
        End If
    End Sub

    Private Async Function ObterTotalRegistrosAsync(Optional filtro As String = "") As Task(Of Integer)
        Dim total As Integer = 0
        Try
            Dim sql As String =
                "SELECT COUNT(*) FROM Visitantes_Fornecedores " &
                "WHERE Nome LIKE @Filtro OR Empresa LIKE @Filtro"

            Using cn As New SqlConnection(connectionString)
                Using cmd As New SqlCommand(sql, cn)
                    cmd.Parameters.AddWithValue("@Filtro", "%" & filtro & "%")
                    Await cn.OpenAsync()
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
        Try
            Dim offset As Integer = (pagina - 1) * registrosPorPagina

            Dim sql As String =
                "SELECT Id, Nome, Empresa, Telefone, Email, Data, Responsavel, Observacao, Almoco, PreConfirmado " &
                "FROM Visitantes_Fornecedores " &
                "WHERE Nome LIKE @Filtro OR Empresa LIKE @Filtro " &
                "ORDER BY Data DESC " &
                "OFFSET @Offset ROWS FETCH NEXT @Limite ROWS ONLY"

            Using cn As New SqlConnection(connectionString)
                Using cmd As New SqlCommand(sql, cn)
                    cmd.Parameters.AddWithValue("@Filtro", "%" & filtro & "%")
                    cmd.Parameters.AddWithValue("@Offset", offset)
                    cmd.Parameters.AddWithValue("@Limite", registrosPorPagina)

                    Dim da As New SqlDataAdapter(cmd)
                    Dim dt As New DataTable()
                    Await cn.OpenAsync()
                    da.Fill(dt)
                    dgvVisitantes.DataSource = dt
                End Using
            End Using

            ConfigurarColunas()
        Catch ex As Exception
            MessageBox.Show("Erro ao carregar dados: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Function

    Private Sub ConfigurarColunas()
        If dgvVisitantes.Columns.Contains("Id") Then dgvVisitantes.Columns("Id").Visible = False

        If dgvVisitantes.Columns.Contains("Nome") Then
            With dgvVisitantes.Columns("Nome")
                .HeaderText = "Nome do Visitante"
                .DisplayIndex = 0
            End With
        End If

        If dgvVisitantes.Columns.Contains("Empresa") Then
            With dgvVisitantes.Columns("Empresa")
                .HeaderText = "Empresa"
                .DisplayIndex = 1
            End With
        End If

        If dgvVisitantes.Columns.Contains("Telefone") Then
            With dgvVisitantes.Columns("Telefone")
                .HeaderText = "Telefone"
                .DisplayIndex = 2
            End With
        End If

        If dgvVisitantes.Columns.Contains("Email") Then
            With dgvVisitantes.Columns("Email")
                .HeaderText = "Email"
                .DisplayIndex = 3
            End With
        End If

        If dgvVisitantes.Columns.Contains("Data") Then
            With dgvVisitantes.Columns("Data")
                .HeaderText = "Data"
                .DisplayIndex = 4
            End With
        End If

        If dgvVisitantes.Columns.Contains("Responsavel") Then
            With dgvVisitantes.Columns("Responsavel")
                .HeaderText = "Responsável"
                .DisplayIndex = 5
            End With
        End If

        If dgvVisitantes.Columns.Contains("Observacao") Then
            With dgvVisitantes.Columns("Observacao")
                .HeaderText = "Observação"
                .DisplayIndex = 6
            End With
        End If

        If dgvVisitantes.Columns.Contains("Almoco") Then
            With dgvVisitantes.Columns("Almoco")
                .HeaderText = "Almoço"
                .DisplayIndex = 7
            End With
        End If

        If dgvVisitantes.Columns.Contains("PreConfirmado") Then
            With dgvVisitantes.Columns("PreConfirmado")
                .HeaderText = "Pré-Confirmado"
                .DisplayIndex = 8
            End With
        End If

        Dim totalCols As Integer = dgvVisitantes.Columns.Count
        If dgvVisitantes.Columns.Contains("Editar") Then
            dgvVisitantes.Columns("Editar").DisplayIndex = totalCols - 3
        End If
        If dgvVisitantes.Columns.Contains("Duplicar") Then
            dgvVisitantes.Columns("Duplicar").DisplayIndex = totalCols - 2
            dgvVisitantes.Columns("Duplicar").Visible = False
        End If
        If dgvVisitantes.Columns.Contains("Eliminar") Then
            dgvVisitantes.Columns("Eliminar").DisplayIndex = totalCols - 1
        End If
    End Sub

    Private Sub AtualizarLabelPagina()
        Dim totalPaginas As Integer = 0
        If totalRegistros > 0 Then
            totalPaginas = CInt(Math.Ceiling(totalRegistros / CDbl(registrosPorPagina)))
        End If
        lblPagina.Text = "Página " & paginaAtual.ToString() &
                         " de " & totalPaginas.ToString() &
                         "   (" & totalRegistros.ToString() & " registos)"
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
        Await CarregarDadosIniciais()
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

    Private Sub dgvVisitantes_CellContentClick(sender As Object,
                                               e As DataGridViewCellEventArgs)
        If e.RowIndex < 0 Then Return
        Dim nomeColuna As String = dgvVisitantes.Columns(e.ColumnIndex).Name

        If nomeColuna = "Editar" Then
            EditarVisitante(e.RowIndex)
        ElseIf nomeColuna = "Duplicar" Then
            ' Coluna mantida, mas escondida
        ElseIf nomeColuna = "Eliminar" Then
            EliminarVisitante(e.RowIndex)
        End If
    End Sub

    Private Async Sub EditarVisitante(rowIndex As Integer)
        Dim dt As DataTable = TryCast(dgvVisitantes.DataSource, DataTable)
        If dt Is Nothing Then Return

        Dim rowView As DataRowView =
            CType(dgvVisitantes.Rows(rowIndex).DataBoundItem, DataRowView)
        Dim linha As DataRow = rowView.Row

        Dim frm As New FormEdicaoVisitante(connectionString, linha)
        If frm.ShowDialog() = DialogResult.OK Then
            Await CarregarDadosPaginaAsync(paginaAtual, filtroNomeEmpresa)
            AtualizarLabelPagina()
            AtualizarEstadoBotoes()
        End If
    End Sub

    Private Async Sub EliminarVisitante(rowIndex As Integer)
        Dim dt As DataTable = TryCast(dgvVisitantes.DataSource, DataTable)
        If dt Is Nothing Then Return

        Dim rowView As DataRowView =
            CType(dgvVisitantes.Rows(rowIndex).DataBoundItem, DataRowView)
        Dim linha As DataRow = rowView.Row

        Dim idVisitante As Integer = CInt(linha("Id"))
        Dim nome As String = linha("Nome").ToString()

        Dim resp As DialogResult =
            MessageBox.Show("Confirmar eliminação de """ & nome & """ ?",
                            "Eliminar", MessageBoxButtons.YesNo,
                            MessageBoxIcon.Warning)

        If resp <> DialogResult.Yes Then Return

        Try
            Using cn As New SqlConnection(connectionString)
                Using cmd As New SqlCommand("DELETE FROM Visitantes_Fornecedores WHERE Id=@Id", cn)
                    cmd.Parameters.AddWithValue("@Id", idVisitante)
                    Await cn.OpenAsync()
                    Await cmd.ExecuteNonQueryAsync()
                End Using
            End Using

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
            MessageBox.Show("Erro ao eliminar: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    '====================== IMPRESSÃO ======================

    Private Sub PreencherDadosImpressao(row As DataGridViewRow)
        nomeVisitante = If(row.Cells("Nome").Value IsNot Nothing,
                           row.Cells("Nome").Value.ToString(), "")
        empresaVisitante = If(row.Cells("Empresa").Value IsNot Nothing,
                              row.Cells("Empresa").Value.ToString(), "")
        telefoneVisitante = If(row.Cells("Telefone").Value IsNot Nothing,
                               row.Cells("Telefone").Value.ToString(), "")
        emailVisitante = If(row.Cells("Email").Value IsNot Nothing,
                            row.Cells("Email").Value.ToString(), "")

        Dim dataVal As Object = row.Cells("Data").Value
        If dataVal IsNot Nothing AndAlso Not IsDBNull(dataVal) Then
            dataVisitante = CDate(dataVal).ToString("dd/MM/yyyy")
        Else
            dataVisitante = ""
        End If

        responsavelVisitante = If(row.Cells("Responsavel").Value IsNot Nothing,
                                  row.Cells("Responsavel").Value.ToString(), "")
        observacaoVisitante = If(row.Cells("Observacao").Value IsNot Nothing,
                                 row.Cells("Observacao").Value.ToString(), "")
        preConfirmadoVisitante = If(row.Cells("PreConfirmado").Value IsNot Nothing,
                                    row.Cells("PreConfirmado").Value.ToString(), "")
    End Sub

    Private Sub PrintFicha()
        If dgvVisitantes.SelectedRows.Count = 0 Then
            MessageBox.Show("Selecione um visitante para imprimir.",
                            "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Information)
            Return
        End If

        Dim row As DataGridViewRow = dgvVisitantes.SelectedRows(0)
        PreencherDadosImpressao(row)

        Dim doc As New PrintDocument()
        AddHandler doc.PrintPage, AddressOf PrintDoc_PrintPage

        Dim dlg As New PrintDialog()
        dlg.Document = doc
        If dlg.ShowDialog() = DialogResult.OK Then
            doc.Print()
        End If

        RemoveHandler doc.PrintPage, AddressOf PrintDoc_PrintPage
        doc.Dispose()
    End Sub

    Private Sub PrintDoc_PrintPage(sender As Object, e As PrintPageEventArgs)
        Dim fonteNegrito As New Font("Arial", 14, FontStyle.Bold)
        Dim fonteNormal As New Font("Arial", 10, FontStyle.Regular)
        Dim fonteObs As New Font("Arial", 9, FontStyle.Italic)
        Dim brush As New SolidBrush(Color.Black)

        Dim x As Integer = 10
        Dim y As Integer = 10

        e.Graphics.DrawString("Visitante", fonteNegrito, brush, x, y)
        y += 30
        e.Graphics.DrawString("Nome: " & nomeVisitante, fonteNormal, brush, x, y)
        y += 25
        e.Graphics.DrawString("Empresa: " & empresaVisitante, fonteNormal, brush, x, y)
        y += 25
        e.Graphics.DrawString("Telefone: " & telefoneVisitante, fonteNormal, brush, x, y)
        y += 25
        e.Graphics.DrawString("Email: " & emailVisitante, fonteNormal, brush, x, y)
        y += 25
        e.Graphics.DrawString("Data: " & dataVisitante, fonteNormal, brush, x, y)
        y += 25
        e.Graphics.DrawString("Responsável: " & responsavelVisitante, fonteNormal, brush, x, y)
        y += 25
        e.Graphics.DrawString("Observação: " & observacaoVisitante, fonteObs, brush, x, y)
        y += 25
        e.Graphics.DrawString("Pré-Confirmado: " & preConfirmadoVisitante, fonteNormal, brush, x, y)

        Dim logoPath As String = Path.Combine(Application.StartupPath, "Imagens", "logo-virt.jpeg")
        If File.Exists(logoPath) Then
            Using img As Image = Image.FromFile(logoPath)
                e.Graphics.DrawImage(img, 350, 40, 80, 120)
            End Using
        End If
    End Sub

    '====================== EXPORTAÇÃO EXCEL ======================

    Private Sub ExportarParaExcel()
        Try
            Dim dlg As New SaveFileDialog()
            dlg.Filter = "Ficheiros Excel (*.xlsx)|*.xlsx"
            dlg.FileName = "Visitantes.xlsx"
            If dlg.ShowDialog() <> DialogResult.OK Then Return

            Dim appExcel As Excel.Application = Nothing
            Dim wb As Excel.Workbook = Nothing
            Dim ws As Excel.Worksheet = Nothing

            appExcel = New Excel.Application()
            appExcel.Visible = False
            appExcel.DisplayAlerts = False

            wb = appExcel.Workbooks.Add()
            ws = CType(wb.Sheets(1), Excel.Worksheet)

            Dim c As Integer
            For c = 0 To dgvVisitantes.Columns.Count - 1
                ws.Cells(1, c + 1) = dgvVisitantes.Columns(c).HeaderText
            Next

            Dim r As Integer
            For r = 0 To dgvVisitantes.Rows.Count - 1
                For c = 0 To dgvVisitantes.Columns.Count - 1
                    Dim val As Object = dgvVisitantes.Rows(r).Cells(c).Value
                    ws.Cells(r + 2, c + 1) = If(val IsNot Nothing, val.ToString(), "")
                Next
            Next

            ws.Columns.AutoFit()
            wb.SaveAs(dlg.FileName)
            wb.Close()
            appExcel.Quit()

            ReleaseComObject(ws)
            ReleaseComObject(wb)
            ReleaseComObject(appExcel)

            MessageBox.Show("Exportação concluída com sucesso.",
                            "Excel", MessageBoxButtons.OK, MessageBoxIcon.Information)
        Catch ex As Exception
            MessageBox.Show("Erro ao exportar para Excel: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    Private Sub ReleaseComObject(ByVal obj As Object)
        Try
            If obj IsNot Nothing Then
                System.Runtime.InteropServices.Marshal.ReleaseComObject(obj)
            End If
        Catch
        Finally
            obj = Nothing
        End Try
    End Sub

    '====================== MENUS / TOOLSTRIP ======================

    Private Sub ExportarExcelToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ExportarExcelToolStripMenuItem.Click
        ExportarParaExcel()
    End Sub

    Private Sub ImprimirToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ImprimirToolStripMenuItem.Click
        PrintFicha()
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
        Dim frm As New Lista_Individual
        frm.Show()
        Close()
    End Sub

    Private Sub ClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ClientesToolStripMenuItem.Click
        Dim frm As New InserirVisitantes()
        frm.Show()
        Me.Close()
    End Sub

    Private Sub MenuToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles MenuToolStripMenuItem1.Click
        Dim frm As New Menu()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaDeClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeClientesToolStripMenuItem.Click
        Dim frm As New ListaClientes()
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

    Private Sub VisitasFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles VisitasFornecedoresToolStripMenuItem.Click
        Dim frm As New InserirVisitantesFornecedores()
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

'====================== FORM DE EDIÇÃO ======================

Public Class FormEdicaoVisitante
    Inherits Form

    Private _connString As String
    Private _idVisitante As Integer

    Private txtNome As TextBox
    Private txtEmpresa As TextBox
    Private txtTelefone As TextBox
    Private txtEmail As TextBox
    Private dtData As DateTimePicker
    Private txtResponsavel As TextBox
    Private txtObservacao As TextBox
    Private cmbAlmoco As ComboBox
    Private cmbPreConfirmado As ComboBox

    ' Para comparação de antes/depois
    Private almocoAntes As String

    Public Sub New(connString As String, linha As DataRow)
        _connString = connString
        _idVisitante = CInt(linha("Id"))
        InicializarComponentes(linha)
    End Sub

    Private Sub InicializarComponentes(linha As DataRow)
        Me.Text = "Editar Visitante Fornecedor"
        Me.Size = New Size(450, 520)
        Me.FormBorderStyle = FormBorderStyle.FixedDialog
        Me.MaximizeBox = False
        Me.MinimizeBox = False
        Me.StartPosition = FormStartPosition.CenterParent

        Dim y As Integer = 20

        Dim lblNome As New Label()
        lblNome.Text = "Nome:"
        lblNome.Left = 20
        lblNome.Top = y
        lblNome.Width = 100
        lblNome.TextAlign = ContentAlignment.MiddleRight
        Me.Controls.Add(lblNome)

        txtNome = New TextBox()
        txtNome.Left = 130
        txtNome.Top = y
        txtNome.Width = 260
        txtNome.Text = linha("Nome").ToString()
        Me.Controls.Add(txtNome)

        y += 35
        Dim lblEmp As New Label()
        lblEmp.Text = "Empresa:"
        lblEmp.Left = 20
        lblEmp.Top = y
        lblEmp.Width = 100
        lblEmp.TextAlign = ContentAlignment.MiddleRight
        Me.Controls.Add(lblEmp)

        txtEmpresa = New TextBox()
        txtEmpresa.Left = 130
        txtEmpresa.Top = y
        txtEmpresa.Width = 260
        txtEmpresa.Text = linha("Empresa").ToString()
        Me.Controls.Add(txtEmpresa)

        y += 35
        Dim lblTel As New Label()
        lblTel.Text = "Telefone:"
        lblTel.Left = 20
        lblTel.Top = y
        lblTel.Width = 100
        lblTel.TextAlign = ContentAlignment.MiddleRight
        Me.Controls.Add(lblTel)

        txtTelefone = New TextBox()
        txtTelefone.Left = 130
        txtTelefone.Top = y
        txtTelefone.Width = 260
        txtTelefone.Text = linha("Telefone").ToString()
        Me.Controls.Add(txtTelefone)

        y += 35
        Dim lblEmail As New Label()
        lblEmail.Text = "Email:"
        lblEmail.Left = 20
        lblEmail.Top = y
        lblEmail.Width = 100
        lblEmail.TextAlign = ContentAlignment.MiddleRight
        Me.Controls.Add(lblEmail)

        txtEmail = New TextBox()
        txtEmail.Left = 130
        txtEmail.Top = y
        txtEmail.Width = 260
        txtEmail.Text = linha("Email").ToString()
        Me.Controls.Add(txtEmail)

        y += 35
        Dim lblData As New Label()
        lblData.Text = "Data:"
        lblData.Left = 20
        lblData.Top = y
        lblData.Width = 100
        lblData.TextAlign = ContentAlignment.MiddleRight
        Me.Controls.Add(lblData)

        dtData = New DateTimePicker()
        dtData.Left = 130
        dtData.Top = y
        dtData.Width = 260
        dtData.Value = CDate(linha("Data"))
        Me.Controls.Add(dtData)

        y += 35
        Dim lblResp As New Label()
        lblResp.Text = "Responsável:"
        lblResp.Left = 20
        lblResp.Top = y
        lblResp.Width = 100
        lblResp.TextAlign = ContentAlignment.MiddleRight
        Me.Controls.Add(lblResp)

        txtResponsavel = New TextBox()
        txtResponsavel.Left = 130
        txtResponsavel.Top = y
        txtResponsavel.Width = 260
        txtResponsavel.Text = linha("Responsavel").ToString()
        Me.Controls.Add(txtResponsavel)

        y += 35
        Dim lblObs As New Label()
        lblObs.Text = "Observação:"
        lblObs.Left = 20
        lblObs.Top = y
        lblObs.Width = 100
        lblObs.TextAlign = ContentAlignment.MiddleRight
        Me.Controls.Add(lblObs)

        txtObservacao = New TextBox()
        txtObservacao.Left = 130
        txtObservacao.Top = y
        txtObservacao.Width = 260
        txtObservacao.Height = 60
        txtObservacao.Multiline = True
        txtObservacao.Text = linha("Observacao").ToString()
        Me.Controls.Add(txtObservacao)

        y += 70
        Dim lblAlm As New Label()
        lblAlm.Text = "Almoço:"
        lblAlm.Left = 20
        lblAlm.Top = y
        lblAlm.Width = 100
        lblAlm.TextAlign = ContentAlignment.MiddleRight
        Me.Controls.Add(lblAlm)

        cmbAlmoco = New ComboBox()
        cmbAlmoco.Left = 130
        cmbAlmoco.Top = y
        cmbAlmoco.Width = 260
        cmbAlmoco.DropDownStyle = ComboBoxStyle.DropDownList
        cmbAlmoco.Items.Add("Sim")
        cmbAlmoco.Items.Add("Não")

        Dim valorAlm As String = linha("Almoco").ToString()
        almocoAntes = valorAlm
        If valorAlm.Equals("Sim", StringComparison.OrdinalIgnoreCase) Then
            cmbAlmoco.SelectedItem = "Sim"
        Else
            cmbAlmoco.SelectedItem = "Não"
        End If

        Me.Controls.Add(cmbAlmoco)

        y += 35
        Dim lblPre As New Label()
        lblPre.Text = "Pré-Confirmado:"
        lblPre.Left = 20
        lblPre.Top = y
        lblPre.Width = 100
        lblPre.TextAlign = ContentAlignment.MiddleRight
        Me.Controls.Add(lblPre)

        cmbPreConfirmado = New ComboBox()
        cmbPreConfirmado.Left = 130
        cmbPreConfirmado.Top = y
        cmbPreConfirmado.Width = 260
        cmbPreConfirmado.DropDownStyle = ComboBoxStyle.DropDownList
        cmbPreConfirmado.Items.Add("SIM")
        cmbPreConfirmado.Items.Add("NAO")
        Dim valorPre As String = linha("PreConfirmado").ToString().ToUpper()
        If valorPre = "SIM" OrElse valorPre = "NAO" Then
            cmbPreConfirmado.SelectedItem = valorPre
        End If
        Me.Controls.Add(cmbPreConfirmado)

        Dim btnGravar As New Button()
        btnGravar.Text = "Gravar"
        btnGravar.Left = 160
        btnGravar.Top = y + 45
        btnGravar.Width = 90
        AddHandler btnGravar.Click, AddressOf BtnGravar_Click
        Me.Controls.Add(btnGravar)

        Dim btnCancelar As New Button()
        btnCancelar.Text = "Cancelar"
        btnCancelar.Left = 260
        btnCancelar.Top = y + 45
        btnCancelar.Width = 90
        btnCancelar.DialogResult = DialogResult.Cancel
        Me.Controls.Add(btnCancelar)

        Me.AcceptButton = btnGravar
        Me.CancelButton = btnCancelar
    End Sub

    Private Async Sub BtnGravar_Click(sender As Object, e As EventArgs)
        Dim almocoDepois As String =
            If(cmbAlmoco.SelectedItem IsNot Nothing,
               cmbAlmoco.SelectedItem.ToString(),
               "Não")

        Try
            Using cn As New SqlConnection(_connString)
                Using cmd As New SqlCommand("
UPDATE Visitantes_Fornecedores
SET Nome=@Nome,
    Empresa=@Empresa,
    Telefone=@Telefone,
    Email=@Email,
    Data=@Data,
    Responsavel=@Responsavel,
    Observacao=@Observacao,
    Almoco=@Almoco,
    PreConfirmado=@PreConfirmado
WHERE Id=@Id", cn)

                    cmd.Parameters.AddWithValue("@Nome", txtNome.Text.Trim())
                    cmd.Parameters.AddWithValue("@Empresa", txtEmpresa.Text.Trim())
                    cmd.Parameters.AddWithValue("@Telefone", txtTelefone.Text.Trim())
                    cmd.Parameters.AddWithValue("@Email", txtEmail.Text.Trim())
                    cmd.Parameters.AddWithValue("@Data", dtData.Value)
                    cmd.Parameters.AddWithValue("@Responsavel", txtResponsavel.Text.Trim())
                    cmd.Parameters.AddWithValue("@Observacao", txtObservacao.Text.Trim())
                    cmd.Parameters.AddWithValue("@Almoco", almocoDepois)
                    cmd.Parameters.AddWithValue("@PreConfirmado",
                                                If(cmbPreConfirmado.SelectedItem IsNot Nothing,
                                                   cmbPreConfirmado.SelectedItem.ToString(),
                                                   "NAO"))
                    cmd.Parameters.AddWithValue("@Id", _idVisitante)

                    Await cn.OpenAsync()
                    Await cmd.ExecuteNonQueryAsync()
                End Using
            End Using

            ' SE ALMOÇO PASSOU DE "Não" PARA "Sim" => ENVIAR EMAIL
            If almocoAntes.Equals("Não", StringComparison.OrdinalIgnoreCase) AndAlso
               almocoDepois.Equals("Sim", StringComparison.OrdinalIgnoreCase) Then

                Try
                    Dim mail As New MailMessage()
                    mail.From = New MailAddress("informatica@socem.pt")
                    mail.To.Add("Refeitorio@socem.pt")
                    mail.Subject = "Aviso: Almoço para Fornecedor"
                    mail.Body =
                        $"O Fornecedor {txtNome.Text.Trim()} da empresa {txtEmpresa.Text.Trim()}, " &
                        $"que vem acompanhado pelo responsável {txtResponsavel.Text.Trim()}, " &
                        $"irá almoçar no dia {dtData.Value.ToShortDateString()}."

                    Dim smtp As New SmtpClient("smtp.office365.com")
                    smtp.Port = 587
                    smtp.Credentials = New System.Net.NetworkCredential("vitor.leonardo@socem.pt", "0L@cao1988")
                    smtp.EnableSsl = True
                    smtp.Send(mail)
                Catch exMail As Exception
                    MessageBox.Show("Erro ao enviar email: " & exMail.Message,
                                    "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                End Try
            End If

            Me.DialogResult = DialogResult.OK
            Me.Close()
        Catch ex As Exception
            MessageBox.Show("Erro ao gravar: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

End Class
