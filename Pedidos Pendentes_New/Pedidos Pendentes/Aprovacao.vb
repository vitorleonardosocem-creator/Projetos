Imports System.Data.SqlClient
Imports System.Drawing.Printing
Imports System.IO
Imports Microsoft.Data.SqlClient
Imports QRCoder

Public Class Aprovacao
    ' Definir variáveis para os dados do visitante
    Dim nomeVisitante As String
    Dim empresaVisitante As String
    Dim telefoneVisitante As String
    Dim emailVisitante As String
    Dim fotoVisitante As Byte()

    ' String de conexão
    Dim conexao As String = "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"

    ' Quando o formulário é carregado
    Private Sub Form1_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        CarregarPedidosPendentes()
    End Sub

    ' Carregar pedidos pendentes na DataGridView
    Private Sub CarregarPedidosPendentes()
        Using con As New SqlConnection(conexao)
            Try
                con.Open()

                Dim query As String = "SELECT Id, Nome, Empresa, Telefone, Email, Data FROM Visitantes WHERE Status = 'Pendente'"
                Using cmd As New SqlCommand(query, con)
                    Using reader As SqlDataReader = cmd.ExecuteReader()
                        dgvPedidosPendentes.Rows.Clear()

                        While reader.Read()
                            dgvPedidosPendentes.Rows.Add(reader("Id"), reader("Nome"), reader("Empresa"), reader("Telefone"), reader("Email"), Convert.ToDateTime(reader("Data")).ToString("dd/MM/yyyy"))
                        End While
                    End Using
                End Using
            Catch ex As Exception
                MessageBox.Show("Erro ao carregar pedidos: " & ex.Message, "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            End Try
        End Using
    End Sub

    ' Botão de Aprovação de pedido
    Private Sub btnAprovar_Click(sender As Object, e As EventArgs) Handles btnAprovar.Click
        If dgvPedidosPendentes.SelectedRows.Count > 0 Then
            Dim pedidoId As Integer = Convert.ToInt32(dgvPedidosPendentes.SelectedRows(0).Cells(0).Value)
            If Not IsDBNull(pedidoId) Then
                ObterDadosVisitante(pedidoId)
                AprovarPedido(pedidoId)
                PrintEtiqueta(fotoVisitante)
                CarregarPedidosPendentes()
                MessageBox.Show("Pedido aprovado com sucesso! A etiqueta será impressa.", "Sucesso", MessageBoxButtons.OK, MessageBoxIcon.Information)
            Else
                MessageBox.Show("ID do pedido não encontrado.", "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error)
            End If
        Else
            MessageBox.Show("Selecione um pedido para aprovar.", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Warning)
        End If
    End Sub

    ' Obter dados do visitante
    Private Sub ObterDadosVisitante(pedidoId As Integer)
        Using con As New SqlConnection(conexao)
            con.Open()
            Dim query As String = "SELECT Nome, Empresa, Telefone, Email, Foto FROM Visitantes WHERE Id = @Id"
            Using cmd As New SqlCommand(query, con)
                cmd.Parameters.AddWithValue("@Id", pedidoId)
                Using reader As SqlDataReader = cmd.ExecuteReader()
                    If reader.Read() Then
                        nomeVisitante = reader("Nome").ToString()
                        empresaVisitante = reader("Empresa").ToString()
                        telefoneVisitante = reader("Telefone").ToString()
                        emailVisitante = reader("Email").ToString()
                        fotoVisitante = If(reader("Foto") Is DBNull.Value, Nothing, CType(reader("Foto"), Byte()))
                    End If
                End Using
            End Using
        End Using
    End Sub

    ' Aprovar o pedido no banco de dados
    Private Sub AprovarPedido(pedidoId As Integer)
        Using con As New SqlConnection(conexao)
            con.Open()
            Dim query As String = "UPDATE Visitantes SET Status = 'Aprovado' WHERE Id = @Id"
            Using cmd As New SqlCommand(query, con)
                cmd.Parameters.AddWithValue("@Id", pedidoId)
                cmd.ExecuteNonQuery()
            End Using
        End Using
    End Sub

    ' Função para imprimir a etiqueta com foto
    Private Sub PrintEtiqueta(foto As Byte())
        Dim PrintDoc As New PrintDocument()
        AddHandler PrintDoc.PrintPage, AddressOf Me.PrintDoc_PrintPage

        Dim printDialog As New PrintDialog()
        printDialog.Document = PrintDoc

        If printDialog.ShowDialog() = DialogResult.OK Then
            PrintDoc.Print()
        End If
    End Sub

    ' Configuração de impressão de etiqueta
    Private Sub PrintDoc_PrintPage(sender As Object, e As PrintPageEventArgs)
        Dim fonte As New Font("Arial", 10)
        Dim brush As New SolidBrush(Color.Black)

        Dim margemSuperior As Integer = 0
        Dim margemEsquerda As Integer = 5

        ' Posição de rotação para a impressão
        Dim centroX As Integer = 70
        Dim centroY As Integer = 105

        e.Graphics.TranslateTransform(centroX, centroY)
        e.Graphics.RotateTransform(90)
        e.Graphics.TranslateTransform(-centroX, -centroY)

        ' Imprime os dados normais (Nome e Empresa na etiqueta)
        Dim checkImagePath As String = "C:\Users\vitor.leonardo\source\repos\Pedidos Pendentes\Pedidos Pendentes\bin\Debug\net8.0-windows\visto.png"

        ' Verifica se a imagem existe antes de tentar carregar
        If File.Exists(checkImagePath) Then
            Dim checkImage As Image = Image.FromFile(checkImagePath)
            Dim larguraCheck As Integer = 20 ' Ajustar o tamanho do ícone
            Dim alturaCheck As Integer = 20
            e.Graphics.DrawImage(checkImage, margemEsquerda + 230, margemSuperior, larguraCheck, alturaCheck)
        Else
            ' Caso a imagem não seja encontrada, exibe o texto como alternativa
            e.Graphics.DrawString("Visitante Aprovado", New Font("Arial", 14, FontStyle.Bold), brush, margemEsquerda, margemSuperior)
        End If

        ' Imprime Nome e Empresa na etiqueta (ajustado para não sobrepor a imagem)
        e.Graphics.DrawString(" " & nomeVisitante, New Font("Arial", 14, FontStyle.Bold), brush, margemEsquerda + 10, margemSuperior)
        e.Graphics.DrawString(" " & empresaVisitante, fonte, brush, margemEsquerda + 10, margemSuperior + 20)

        ' Criar um QR Code no formato vCard com apenas nome, telefone e e-mail
        Dim vCard As String = $"BEGIN:VCARD{vbCrLf}" &
                          $"VERSION:3.0{vbCrLf}" &
                          $"FN:{nomeVisitante}{vbCrLf}" &
                          $"TEL:+{telefoneVisitante.TrimStart("+"c)}{vbCrLf}" &
                          $"EMAIL:{emailVisitante}{vbCrLf}" &
                          $"END:VCARD"

        Dim qrCodeImage As Image = GerarQRCode(vCard)

        ' Imprimir o QR Code na etiqueta
        If qrCodeImage IsNot Nothing Then
            e.Graphics.DrawImage(qrCodeImage, margemEsquerda + 30, margemSuperior + 50, 120, 120)
        End If

        ' Imprimir a foto do visitante se disponível
        If fotoVisitante IsNot Nothing Then
            Dim imagem As Image = Nothing
            Using ms As New MemoryStream(fotoVisitante)
                imagem = Image.FromStream(ms)
            End Using
            e.Graphics.DrawImage(imagem, margemEsquerda + 170, margemSuperior + 50, 170, 130)
        End If

        ' Imprimir logo SOCEM
        Dim logo As Image = Image.FromFile("C:\Users\vitor.leonardo\source\repos\Pedidos Pendentes\Pedidos Pendentes\bin\Debug\net8.0-windows\logo-virt.jpeg")
        ' Defina a largura e altura desejada
        Dim larguraImagem As Integer = 40  ' Largura do logo em pixels (ajuste conforme necessário)
        Dim alturaImagem As Integer = 140   ' Altura do logo em pixels (ajuste conforme necessário)
        ' Agora, desenhe a imagem com as novas dimensões
        e.Graphics.DrawImage(logo, margemEsquerda - 40, margemSuperior + 30, larguraImagem, alturaImagem)


        e.Graphics.ResetTransform()
    End Sub

    Private Function GerarQRCode(texto As String) As Image
        Try
            Dim qrGenerator As New QRCodeGenerator()
            Dim qrCodeData As QRCodeData = qrGenerator.CreateQrCode(texto, QRCodeGenerator.ECCLevel.Q)
            Dim qrCode As New QRCode(qrCodeData)
            Return qrCode.GetGraphic(5)
        Catch ex As Exception
            MessageBox.Show("Erro ao gerar QR Code: " & ex.Message)
            Return Nothing
        End Try
    End Function

    ' Função de cancelamento
    Private Sub btnCancelar_Click(sender As Object, e As EventArgs) Handles btnCancelar.Click
        dgvPedidosPendentes.ClearSelection()
        lblStatus.Text = "Selecione um pedido para aprovar."
    End Sub

    Private Sub MenuToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles MenuToolStripMenuItem.Click

    End Sub

    Private Sub SairToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles SairToolStripMenuItem.Click
        Application.Exit()
    End Sub

    Private Sub MenuToolStripMenuItem2_Click(sender As Object, e As EventArgs) Handles MenuToolStripMenuItem2.Click
        Dim frm As New Menu()

        frm.Show()
        Me.Close()
    End Sub
    Private Sub ListaToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaToolStripMenuItem.Click
        Dim frm As New ListaVisitantes()

        frm.Show()
        Me.Close()
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
End Class
