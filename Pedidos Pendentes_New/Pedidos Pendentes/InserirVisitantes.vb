Imports System.Data.SqlClient
Imports System.Globalization
Imports System.Net.Mail
Imports System.Text.RegularExpressions
Imports Microsoft.Data.SqlClient
Imports System.Drawing
Imports System.Drawing.Printing

Public Class InserirVisitantes

    ' String de conexão com o banco de dados
    Private ReadOnly connString As String =
        "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"

    ' Coleção para autocomplete dos nomes
    Private nomesVisitantes As AutoCompleteStringCollection =
        New AutoCompleteStringCollection()

    ' Guarda o IdCliente associado ao nome escolhido (pode ser Nothing)
    Private idClienteSelecionado As Integer?

    ' Variáveis para impressão da etiqueta (como em Fornecedores)
    Private WithEvents printDocEtiqueta As New PrintDocument
    Private dataEtiqueta As Date
    Private responsavelEtiqueta As String

    '======================== GRAVAR VISITANTE ========================

    Private Sub btnGravar_Click(sender As Object, e As EventArgs) Handles btnGravar.Click
        ' Normalizar texto
        Dim nome As String = txtNome.Text.Trim()
        Dim empresa As String = txtEmpresa.Text.Trim()
        Dim telefoneTexto As String = txtTelefone.Text.Trim()
        Dim email As String = txtEmail.Text.Trim()
        Dim responsavel As String = ComboBoxResponsavel.Text.Trim()
        Dim observacao As String = txtObservacao.Text.Trim()

        ' 1. Validações dos campos obrigatórios (exceto data)
        If String.IsNullOrWhiteSpace(nome) OrElse
           String.IsNullOrWhiteSpace(empresa) OrElse
           String.IsNullOrWhiteSpace(telefoneTexto) OrElse
           String.IsNullOrWhiteSpace(email) Then

            MessageBox.Show("Por favor, preencha Nome, Empresa, Telefone e Email.",
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        ' 2. Validação do campo Responsável
        If String.IsNullOrWhiteSpace(responsavel) Then
            MessageBox.Show("Por favor, preencha o campo Responsável.",
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        ' 3. Validação do telefone (apenas dígitos e espaços)
        If Not Regex.IsMatch(telefoneTexto, "^[\d\s]+$") Then
            MessageBox.Show("O telefone deve conter apenas números e espaços.",
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        ' 4. Validação de email com regex simples
        Dim padraoEmail As String = "^[^@\s]+@[^@\s]+\.[^@\s]+$"
        If Not Regex.IsMatch(email, padraoEmail) Then
            MessageBox.Show("O email introduzido não é válido.",
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Exit Sub
        End If

        ' 5. Definir valor para almoço conforme checkbox
        Dim valorAlmoco As String = If(chkAlmoco.Checked, "Sim", "Não")

        ' 6. Obter a data selecionada no DateTimePicker (sem tempo)
        Dim dataValida As DateTime = Date1.Value.Date

        ' 7. Se múltiplos dias, validar que DataFim >= DataInicio
        Dim dataFimValida As DateTime = Date1.Value.Date
        If chkMultiplosDias.Checked Then
            dataFimValida = Date2.Value.Date
            If dataFimValida < dataValida Then
                MessageBox.Show("A data de fim não pode ser anterior à data de início.",
                                "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
                Exit Sub
            End If
        End If

        '======================== INSERÇÃO NA BD ========================

        Try
            Using conn As New SqlConnection(connString)
                conn.Open()

                Dim sql As String =
                    "INSERT INTO Visitantes " &
                    "(Nome, Empresa, Telefone, Email, Data, Responsavel, Observacao, Almoco, IdCliente) " &
                    "VALUES (@Nome, @Empresa, @Telefone, @Email, @Data, @Responsavel, @Observacao, @Almoco, @IdCliente)"

                Dim valorIdCliente As Object = If(idClienteSelecionado.HasValue, CObj(idClienteSelecionado.Value), DBNull.Value)

                ' Cria um registo por cada dia entre dataValida e dataFimValida
                Dim dataAtual As DateTime = dataValida
                Do While dataAtual <= dataFimValida
                    Using cmd As New SqlCommand(sql, conn)
                        cmd.Parameters.AddWithValue("@Nome", nome)
                        cmd.Parameters.AddWithValue("@Empresa", empresa)
                        cmd.Parameters.AddWithValue("@Telefone", telefoneTexto)
                        cmd.Parameters.AddWithValue("@Email", email)
                        cmd.Parameters.AddWithValue("@Data", dataAtual)
                        cmd.Parameters.AddWithValue("@Responsavel", responsavel)
                        cmd.Parameters.AddWithValue("@Observacao", observacao)
                        cmd.Parameters.AddWithValue("@Almoco", valorAlmoco)
                        cmd.Parameters.AddWithValue("@IdCliente", valorIdCliente)
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
                    mail.To.Add("Refeitorio@socem.pt")
                    mail.Subject = "Aviso: Acesso ao Almoço para Cliente"

                    Dim periodoTexto As String
                    If dataFimValida > dataValida Then
                        periodoTexto = $"de {dataValida.ToShortDateString()} a {dataFimValida.ToShortDateString()}"
                    Else
                        periodoTexto = $"no dia {dataValida.ToShortDateString()}"
                    End If
                    mail.Body = String.Format(
                        "O Cliente {0} da empresa {1}, que vem acompanhado pelo responsável {2}, " &
                        "vai ter acesso ao almoço {3}.",
                        nome,
                        empresa,
                        responsavel,
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

            MessageBox.Show("Visitante inserido com sucesso!",
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
        idClienteSelecionado = Nothing
        txtNome.Focus()
    End Sub

    '======================== LOAD / AUTOCOMPLETE ========================

    Private Sub InserirVisitantes_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        CarregarNomesAutocomplete()
    End Sub

    Private Sub CarregarNomesAutocomplete()
        Try
            nomesVisitantes.Clear()

            Using conn As New SqlConnection(connString)
                conn.Open()
                Dim sql As String = "SELECT DISTINCT Nome FROM Clientes ORDER BY Nome"
                Using cmd As New SqlCommand(sql, conn)
                    Using reader As SqlDataReader = cmd.ExecuteReader()
                        While reader.Read()
                            nomesVisitantes.Add(reader("Nome").ToString())
                        End While
                    End Using
                End Using
            End Using

            txtNome.AutoCompleteMode = AutoCompleteMode.SuggestAppend
            txtNome.AutoCompleteSource = AutoCompleteSource.CustomSource
            txtNome.AutoCompleteCustomSource = nomesVisitantes

        Catch ex As Exception
            MessageBox.Show("Erro ao carregar nomes para autocomplete: " & ex.Message,
                            "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    '======================== AUTOPREENCHER CLIENTE ========================

    Private Sub txtNome_Leave(sender As Object, e As EventArgs) Handles txtNome.Leave
        Try
            Dim nomePesquisado As String = txtNome.Text.Trim()
            If String.IsNullOrEmpty(nomePesquisado) Then
                idClienteSelecionado = Nothing
                Exit Sub
            End If

            Using conn As New SqlConnection(connString)
                conn.Open()
                Dim sql As String =
                    "SELECT TOP 1 IdCliente, Empresa, Telefone, Email " &
                    "FROM Clientes " &
                    "WHERE Nome = @Nome " &
                    "ORDER BY IdCliente DESC"

                Using cmd As New SqlCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@Nome", nomePesquisado)

                    Using reader As SqlDataReader = cmd.ExecuteReader()
                        If reader.Read() Then
                            idClienteSelecionado = CInt(reader("IdCliente"))
                            txtEmpresa.Text = reader("Empresa").ToString()
                            txtTelefone.Text = reader("Telefone").ToString()
                            txtEmail.Text = reader("Email").ToString()
                        Else
                            idClienteSelecionado = Nothing
                        End If
                    End Using
                End Using
            End Using

        Catch ex As Exception
            MessageBox.Show("Erro ao buscar dados do cliente: " & ex.Message,
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
    'If chkAlmoco.Checked Then
    'If String.IsNullOrWhiteSpace(ComboBoxResponsavel.Text) OrElse String.IsNullOrWhiteSpace(txtEmpresa.Text) Then
    '           chkAlmoco.Checked = False
    '          MessageBox.Show("Preencha Responsável e Empresa para imprimir etiqueta.", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Warning)
    'Exit Sub
    'End If

    '       dataEtiqueta = Date1.Value.Date
    '      responsavelEtiqueta = ComboBoxResponsavel.Text.Trim()

    'Try
    ' FORÇA impressora específica "Brother QL-720NW (cópia 1)"
    '           printDocEtiqueta.PrinterSettings.PrinterName = "Brother QL-720NW (cópia 1)"

    ' Verifica se impressora existe
    'If Not printDocEtiqueta.PrinterSettings.IsValid Then
    'Throw New Exception("Impressora 'Brother QL-720NW (cópia 1)' não encontrada!")
    'End If

    '           printDocEtiqueta.Print()
    '          MessageBox.Show("Etiqueta impressa na Brother QL-720NW (cópia 1)!", "Sucesso", MessageBoxButtons.OK, MessageBoxIcon.Information)
    'Catch ex As Exception
    '           MessageBox.Show("Erro: " & ex.Message & vbCrLf &
    '                          "Verifique se 'Brother QL-720NW (cópia 1)' está instalada/online.",
    '                         "Erro Impressão", MessageBoxButtons.OK, MessageBoxIcon.Error)
    '        chkAlmoco.Checked = False
    'End Try
    'End If
    'End Sub '

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

        ' LOGO SOCEM - tenta carregar de Application.StartupPath\socem.jpg
        Try
            Dim logoPath As String = IO.Path.Combine(Application.StartupPath, "socem.jpg")
            If IO.File.Exists(logoPath) Then
                Using logo As Image = Image.FromFile(logoPath)
                    ' Exemplo: zona superior direita da etiqueta (ajusta se precisares)
                    g.DrawImage(logo, 35, 2, 12, 8) ' x=35mm, y=2mm, 12x8mm
                End Using
            End If
        Catch
            ' Ignora falha de logo
        End Try

        ' Empresa topo esquerdo
        g.DrawString("Empresa: Socem ED", font7ptBold, brushTexto, 2, 2)

        ' Referência
        g.DrawString("Ref.Socem: Socem EDref_4920", font7ptBold, brushTexto, 2, 6)

        ' Data validade - meio
        g.DrawString("Data:", font7pt, brushTexto, 2, 11)
        g.DrawString(dataEtiqueta.ToString("dd/MM/yyyy"), font7ptBold, brushTexto, 8, 11)

        ' Nº almoços + Nome visitante - centro baixo
        g.DrawString("Nº de almoços: 1", font7ptBold, brushTexto, 2, 19)
        g.DrawString("Nome Visitante: " & txtNome.Text.Trim(), font7pt, brushTexto, 2, 22)

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
        Dim frm As New ListaClientes()
        frm.Show()
        Me.Hide()
    End Sub

    ' Eventos vazios mantidos para o designer
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

    Private Sub ComboBoxResponsavel_SelectedIndexChanged(sender As Object, e As EventArgs) Handles ComboBoxResponsavel.SelectedIndexChanged

    End Sub
End Class
