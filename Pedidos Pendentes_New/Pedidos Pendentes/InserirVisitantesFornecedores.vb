Imports System.Data.SqlClient
Imports System.Globalization
Imports System.Net.Mail
Imports System.Text.RegularExpressions
Imports Microsoft.Data.SqlClient
Imports System.Drawing
Imports System.Drawing.Printing

Public Class InserirVisitantesFornecedores

    ' String de conexão com o banco de dados
    Private ReadOnly connString As String =
        "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"

    ' Coleção para autocomplete dos nomes
    Private nomesVisitantes_Fornecedores As AutoCompleteStringCollection =
        New AutoCompleteStringCollection()

    ' Guarda o Id associado ao nome escolhido (pode ser Nothing)
    Private IdSelecionado As Integer?

    ' Variáveis para impressão da etiqueta
    Private WithEvents printDocEtiqueta As New PrintDocument
    Private dataEtiqueta As Date
    Private responsavelEtiqueta As String

    '======================== GRAVAR VISITANTE ========================

    Private Sub btnGravar_Click(sender As Object, e As EventArgs) Handles btnGravar.Click
        '----------------- Validações -----------------

        If String.IsNullOrWhiteSpace(txtNome.Text) OrElse
       String.IsNullOrWhiteSpace(txtEmpresa.Text) OrElse
       String.IsNullOrWhiteSpace(txtTelefone.Text) OrElse
       String.IsNullOrWhiteSpace(txtEmail.Text) Then

            MessageBox.Show("Por favor, preencha todos os campos obrigatórios.",
                        "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        If String.IsNullOrWhiteSpace(ComboBoxResponsavel.Text) Then
            MessageBox.Show("Por favor, preencha o campo Responsável.",
                        "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        ' Telefone: apenas dígitos e espaços
        Dim telefone As String = txtTelefone.Text.Trim()
        If Not Regex.IsMatch(telefone, "^[\d\s]+$") Then
            MessageBox.Show("O telefone deve conter apenas números e espaços.",
                        "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        ' Email: validação simples com regex
        Dim email As String = txtEmail.Text.Trim()
        Dim padraoEmail As String = "^[^@\s]+@[^@\s]+\.[^@\s]+$"
        If Not Regex.IsMatch(email, padraoEmail) Then
            MessageBox.Show("O email introduzido não é válido.",
                        "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        ' Valor do almoço (Sim/Não) conforme checkbox
        Dim valorAlmoco As String = If(chkAlmoco.Checked, "Sim", "Não")

        ' Data (só a parte da data, sem horas)
        Dim dataValida As DateTime = Date1.Value.Date

        ' Se múltiplos dias, validar que DataFim >= DataInicio
        Dim dataFimValida As DateTime = dataValida
        If chkMultiplosDias.Checked Then
            dataFimValida = Date2.Value.Date
            If dataFimValida < dataValida Then
                MessageBox.Show("A data de fim não pode ser anterior à data de início.",
                                "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                Exit Sub
            End If
        End If

        '----------------- Inserção na BD -----------------

        Try
            Using conn As New SqlConnection(connString)
                conn.Open()

                Dim sql As String =
                "INSERT INTO Visitantes_Fornecedores " &
                "(IdFornecedor, Nome, Empresa, Telefone, Email, Data, Responsavel, Observacao, Almoco) " &
                "VALUES (@IdFornecedor, @Nome, @Empresa, @Telefone, @Email, @Data, @Responsavel, @Observacao, @Almoco)"

                Dim valorIdFornecedor As Object = If(IdSelecionado.HasValue, CObj(IdSelecionado.Value), DBNull.Value)

                ' Cria um registo por cada dia entre dataValida e dataFimValida
                Dim dataAtual As DateTime = dataValida
                Do While dataAtual <= dataFimValida
                    Using cmd As New SqlCommand(sql, conn)
                        cmd.Parameters.AddWithValue("@Nome", txtNome.Text.Trim())
                        cmd.Parameters.AddWithValue("@Empresa", txtEmpresa.Text.Trim())
                        cmd.Parameters.AddWithValue("@Telefone", telefone)
                        cmd.Parameters.AddWithValue("@Email", email)
                        cmd.Parameters.AddWithValue("@Data", dataAtual)
                        cmd.Parameters.AddWithValue("@Responsavel", ComboBoxResponsavel.Text.Trim())
                        cmd.Parameters.AddWithValue("@Observacao", txtObservacao.Text.Trim())
                        cmd.Parameters.AddWithValue("@Almoco", valorAlmoco)
                        cmd.Parameters.AddWithValue("@IdFornecedor", valorIdFornecedor)
                        cmd.ExecuteNonQuery()
                    End Using
                    dataAtual = dataAtual.AddDays(1)
                Loop
            End Using

            '======================== EMAIL (SE ALMOÇO = SIM) ========================
            If valorAlmoco = "Sim" Then
                Try
                    Dim mail As New MailMessage()
                    mail.From = New MailAddress("report.socem@socem.pt")
                    mail.To.Add("refeitorio@socem.pt")
                    mail.Subject = "Aviso: Acesso ao Almoço para Fornecedor"

                    Dim periodoTexto As String
                    If dataFimValida > dataValida Then
                        periodoTexto = $"de {dataValida.ToShortDateString()} a {dataFimValida.ToShortDateString()}"
                    Else
                        periodoTexto = $"no dia {dataValida.ToShortDateString()}"
                    End If
                    mail.Body = String.Format(
                    "O Fornecedor {0} da empresa {1}, que vem acompanhado pelo responsável {2}, " &
                    "vai ter acesso ao almoço {3}.",
                    txtNome.Text.Trim(),
                    txtEmpresa.Text.Trim(),
                    ComboBoxResponsavel.Text.Trim(),
                    periodoTexto
                )

                    Dim smtp As New SmtpClient("smtp.office365.com")
                    smtp.Port = 587
                    smtp.Credentials = New System.Net.NetworkCredential("report.socem@socem.pt", "R3portS0c$m")
                    smtp.EnableSsl = True
                    smtp.Send(mail)
                Catch exMail As Exception
                    MessageBox.Show("Erro ao enviar email: " & exMail.Message,
                                "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                End Try
            End If

            MessageBox.Show("Fornecedor inserido com sucesso!",
                        "Sucesso", MessageBoxButtons.OK, MessageBoxIcon.Information)

            LimparCampos()

        Catch ex As Exception
            MessageBox.Show("Erro ao inserir dados: " & ex.Message,
                        "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    Private Sub LimparCampos()
        txtNome.Clear()
        txtEmpresa.Clear()
        txtTelefone.Clear()
        txtEmail.Clear()
        ComboBoxResponsavel.ResetText()
        txtObservacao.Clear()
        chkAlmoco.Checked = False
        chkMultiplosDias.Checked = False
        Date1.Value = DateTime.Now
        Date2.Value = DateTime.Now
        Date2.Enabled = False
        lblDataFim.Enabled = False
        IdSelecionado = Nothing
    End Sub

    '======================== LOAD / AUTOCOMPLETE ========================

    Private Sub InserirVisitantesFornecedores_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        CarregarNomesAutocomplete()
    End Sub

    Private Sub CarregarNomesAutocomplete()
        Try
            nomesVisitantes_Fornecedores.Clear()

            Using conn As New SqlConnection(connString)
                conn.Open()
                Dim sql As String = "SELECT DISTINCT Nome FROM Fornecedores ORDER BY Nome"
                Using cmd As New SqlCommand(sql, conn)
                    Using reader As SqlDataReader = cmd.ExecuteReader()
                        While reader.Read()
                            nomesVisitantes_Fornecedores.Add(reader("Nome").ToString())
                        End While
                    End Using
                End Using
            End Using

            txtNome.AutoCompleteMode = AutoCompleteMode.SuggestAppend
            txtNome.AutoCompleteSource = AutoCompleteSource.CustomSource
            txtNome.AutoCompleteCustomSource = nomesVisitantes_Fornecedores

        Catch ex As Exception
            MessageBox.Show("Erro ao carregar nomes para autocomplete: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    '======================== AUTOPREENCHER FORNECEDOR ========================

    Private Sub txtNome_Leave(sender As Object, e As EventArgs) Handles txtNome.Leave
        Try
            Dim nomePesquisado As String = txtNome.Text.Trim()
            If String.IsNullOrEmpty(nomePesquisado) Then
                IdSelecionado = Nothing
                Exit Sub
            End If

            Using conn As New SqlConnection(connString)
                conn.Open()
                Dim sql As String =
                    "SELECT TOP 1 Id, Empresa, Telefone, Email " &
                    "FROM Fornecedores " &
                    "WHERE Nome = @Nome " &
                    "ORDER BY Id DESC"

                Using cmd As New SqlCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@Nome", nomePesquisado)

                    Using reader As SqlDataReader = cmd.ExecuteReader()
                        If reader.Read() Then
                            IdSelecionado = CInt(reader("Id"))
                            txtEmpresa.Text = reader("Empresa").ToString()
                            txtTelefone.Text = reader("Telefone").ToString()
                            txtEmail.Text = reader("Email").ToString()
                        Else
                            ' Não existe fornecedor com esse nome: deixa o utilizador preencher tudo
                            IdSelecionado = Nothing
                        End If
                    End Using
                End Using
            End Using

        Catch ex As Exception
            MessageBox.Show("Erro ao buscar dados do Fornecedor: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    '======================== MÚLTIPLOS DIAS ========================

    Private Sub chkMultiplosDias_CheckedChanged(sender As Object, e As EventArgs) Handles chkMultiplosDias.CheckedChanged
        Dim ativo As Boolean = chkMultiplosDias.Checked
        Date2.Enabled = ativo
        lblDataFim.Enabled = ativo
        If Not ativo Then
            Date2.Value = Date1.Value
        End If
    End Sub

    '======================== IMPRESSÃO ETIQUETA ALMOÇO ========================

    ' Private Sub chkAlmoco_CheckedChanged(sender As Object, e As EventArgs) Handles chkAlmoco.CheckedChanged
    '    If chkAlmoco.Checked Then
    '     If String.IsNullOrWhiteSpace(ComboBoxResponsavel.Text) OrElse String.IsNullOrWhiteSpace(txtEmpresa.Text) Then
    '        chkAlmoco.Checked = False
    '        MessageBox.Show("Preencha Responsável e Empresa para imprimir etiqueta.", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Warning)
    '        Exit Sub
    '   End If

    '   dataEtiqueta = Date1.Value.Date
    '  responsavelEtiqueta = ComboBoxResponsavel.Text.Trim()

    '  Try
    ' FORÇA impressora específica "Brother QL-720NW (cópia 1)"
    '     printDocEtiqueta.PrinterSettings.PrinterName = "Brother QL-720NW (cópia 1)"

    ' Verifica se impressora existe
    '   If Not printDocEtiqueta.PrinterSettings.IsValid Then
    '       Throw New Exception("Impressora 'Brother QL-720NW (cópia 1)' não encontrada!")
    '   End If

    '   printDocEtiqueta.Print()
    '  MessageBox.Show("Etiqueta impressa na Brother QL-720NW (cópia 1)!", "Sucesso", MessageBoxButtons.OK, MessageBoxIcon.Information)
    '  Catch ex As Exception
    '  MessageBox.Show("Erro: " & ex.Message & vbCrLf & "Verifique se 'Brother QL-720NW (cópia 1)' está instalada/online.", "Erro Impressão", MessageBoxButtons.OK, MessageBoxIcon.Error)
    '  chkAlmoco.Checked = False
    'End Try
    'End If
    'End Sub


    Private Sub printDocEtiqueta_PrintPage(sender As Object, e As PrintPageEventArgs) Handles printDocEtiqueta.PrintPage
        ' Configura tamanho fixo da etiqueta: 5cm largura x 3cm altura
        e.PageSettings.PaperSize = New PaperSize("EtiquetaAlmoco", 197, 118) ' 197=5cm, 118=3cm
        e.PageSettings.Margins.Left = 0
        e.PageSettings.Margins.Right = 0
        e.PageSettings.Margins.Top = 0
        e.PageSettings.Margins.Bottom = 0

        Dim g As Graphics = e.Graphics
        g.PageUnit = GraphicsUnit.Millimeter

        ' Área de impressão: 48mm x 32mm
        Dim rectEtiqueta As New RectangleF(1, 1, 48, 32)

        ' Fundo branco e moldura preta
        g.FillRectangle(Brushes.White, rectEtiqueta)
        g.DrawRectangle(New Pen(Color.Black, 0.5), 1, 1, 48, 32)

        ' Fonte única: Arial 7pt para TUDO
        Dim font7ptBold As New Font("Arial", 7, FontStyle.Bold)
        Dim font7pt As New Font("Arial", 7, FontStyle.Regular)
        Dim brushTexto As New SolidBrush(Color.Black)

        ' LOGO SOCEM - topo direito (carrega de bin/Debug/net8.0-windows/socem.jpg)
        Try
            Dim logoPath As String = IO.Path.Combine(Application.StartupPath, "socem.jpg")
            If IO.File.Exists(logoPath) Then
                Dim logo As Image = Image.FromFile(logoPath)
                ' Redimensiona logo para 12x8mm topo direito
                g.DrawImage(logo, 1, 38, 48, 8)
                logo.Dispose()
            End If
        Catch
            ' Logo não encontrada - ignora silenciosamente
        End Try

        ' Empresa topo esquerdo
        g.DrawString("Empresa: Socem ED", font7ptBold, brushTexto, 2, 2)

        ' Rerencia
        g.DrawString("Ref.Socem: Socem EDref_4920", font7ptBold, brushTexto, 2, 6)

        ' Data validade - meio
        g.DrawString("Data:", font7pt, brushTexto, 2, 11)
        g.DrawString(dataEtiqueta.ToString("dd/MM/yyyy"), font7ptBold, brushTexto, 8, 11)

        ' Nº almoços + Nome visitante - centro baixo
        g.DrawString("Nº de almoços: 1", font7ptBold, brushTexto, 2, 19)
        g.DrawString("Nome Visitante: " & txtNome.Text.Trim(), font7pt, brushTexto, 2, 22) ' Nome do TextBox

        ' Requisitante - rodapé
        g.DrawString("Requisitante:", font7ptBold, brushTexto, 2, 26)
        g.DrawString(responsavelEtiqueta, font7pt, brushTexto, 2, 28)

        ' Limpeza
        font7ptBold.Dispose()
        font7pt.Dispose()
        brushTexto.Dispose()

        e.HasMorePages = False
    End Sub


    '======================== MENUS / NAVEGAÇÃO ========================

    Private Sub ArovarOuRejeitarToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ArovarOuRejeitarToolStripMenuItem.Click
        Dim frm As New Aprovacao()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub SairToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles SairToolStripMenuItem.Click
        Application.Exit()
    End Sub

    Private Sub ListaToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaToolStripMenuItem.Click
        Dim frm As New ListaVisitantes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub GraficoTotalVisitantesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles GraficoTotalVisitantesToolStripMenuItem.Click
        Dim frm As New Grafico_Total_Visitantes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ListaComFotoToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaComFotoToolStripMenuItem.Click
        Dim frm As New Lista_Individual()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub GraficoEmpresasToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles GraficoEmpresasToolStripMenuItem.Click
        Dim frm As New Grafico_Empresas()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub IrParaOMenuToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles IrParaOMenuToolStripMenuItem.Click
        Dim frm As New Menu()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ClientesToolStripMenuItem.Click
        Dim frm As New InserirVisitantes()
        frm.Show()
        Me.Close()
    End Sub

    Private Sub ListaDeClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeClientesToolStripMenuItem.Click
        Dim frm As New Clientes()
        frm.Show()
        Me.Hide()
    End Sub

    ' Eventos vazios mantidos para compatibilidade com o designer
    Private Sub txtEmpresa_TextChanged(sender As Object, e As EventArgs) Handles txtEmpresa.TextChanged
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

    Private Sub ClientesToolStripMenuItem2_Click(sender As Object, e As EventArgs) Handles ClientesToolStripMenuItem2.Click
        Dim frm As New ListaClientes()
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
