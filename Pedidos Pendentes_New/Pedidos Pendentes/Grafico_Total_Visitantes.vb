Imports System.Data.SqlClient
Imports Microsoft.Data.SqlClient
Imports OxyPlot
Imports OxyPlot.Axes
Imports OxyPlot.Series
Imports OxyPlot.WindowsForms

Public Class Grafico_Total_Visitantes

    Private Sub Grafico_Total_Visitantes_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        ' Criar o TableLayoutPanel e configurar a divisão do formulário
        Dim tableLayout As New TableLayoutPanel() With {
            .Dock = DockStyle.Fill, ' O TableLayoutPanel vai preencher todo o formulário
            .RowCount = 2, ' Duas linhas: uma para o MenuStrip e outra para o gráfico
            .ColumnCount = 1 ' Apenas uma coluna
        }

        ' Configurar a altura da primeira linha (MenuStrip) para o seu tamanho
        tableLayout.RowStyles.Add(New RowStyle(SizeType.AutoSize)) ' A linha do MenuStrip terá um tamanho automático

        ' Configurar a segunda linha (para o gráfico) para ocupar o espaço restante
        tableLayout.RowStyles.Add(New RowStyle(SizeType.Percent, 100)) ' O gráfico vai ocupar o restante do espaço

        ' Adicionar o MenuStrip à primeira linha
        Me.Controls.Add(tableLayout)
        tableLayout.Controls.Add(MenuStrip1, 0, 0)

        ' Criar o modelo de gráfico
        Dim plotModel As New PlotModel() With {
            .Title = "Número Total de Visitantes"
        }

        ' Criar a série de barras verticais
        Dim barSeries As New BarSeries() With {
            .Title = "Visitantes",
            .StrokeThickness = 1,
            .FillColor = OxyColor.FromRgb(0, 128, 255),
            .IsStacked = False ' Não empilhar as barras
        }

        ' Definir a string de conexão (ajuste para o seu banco de dados)
        Dim connectionString As String = "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"

        ' Consultar os dados para contar o total de visitantes
        Dim query As String = "SELECT COUNT(Id) AS TotalVisitantes FROM Visitantes"

        ' Usar SqlConnection e SqlCommand para obter os dados
        Using conn As New SqlConnection(connectionString)
            Using cmd As New SqlCommand(query, conn)
                conn.Open()

                ' Ler o dado e adicionar ao gráfico
                Using reader As SqlDataReader = cmd.ExecuteReader()
                    If reader.Read() Then
                        ' Obter o total de visitantes
                        Dim totalVisitantes As Integer = Convert.ToInt32(reader("TotalVisitantes"))

                        ' Verificar se o valor está correto
                        MessageBox.Show("Total de Visitantes: " & totalVisitantes.ToString())

                        ' Adicionar o valor à série de barras (único valor para a barra)
                        barSeries.Items.Add(New BarItem() With {.Value = totalVisitantes})
                    End If
                End Using
            End Using
        End Using

        ' Configurar o eixo Y (vertical) para ser categórico (apenas uma categoria)
        Dim categoryAxisY As New CategoryAxis() With {
            .Position = AxisPosition.Left, ' Eixo Y (vertical)
            .Title = "Visitantes"
        }
        categoryAxisY.Labels.Add("Total") ' Adiciona apenas uma categoria "Total" para a barra

        ' Configurar o eixo X (horizontal) para ser numérico
        Dim linearAxisX As New LinearAxis() With {
            .Position = AxisPosition.Bottom, ' Eixo X (horizontal)
            .Title = "Total de Visitantes",
            .MajorStep = 1, ' Passo maior de 1 para garantir números inteiros
            .MinorStep = 1, ' Passo menor também de 1
            .StringFormat = "0", ' Mostrar números inteiros (sem casas decimais)
            .Minimum = 0 ' Define o mínimo como 0 para o eixo X
        }

        ' Adicionar os eixos ao gráfico
        plotModel.Axes.Add(categoryAxisY) ' Eixo Y categórico
        plotModel.Axes.Add(linearAxisX) ' Eixo X numérico

        ' Adicionar a série de barras ao gráfico
        plotModel.Series.Add(barSeries)

        ' Criar o controle PlotView para exibir o gráfico
        Dim plotView As New PlotView() With {
            .Model = plotModel,
            .Dock = DockStyle.Fill ' O gráfico vai preencher o restante do formulário
        }

        ' Criar um painel para o gráfico
        Dim panel As New Panel() With {
            .Dock = DockStyle.Fill ' O painel vai preencher o restante do espaço
        }

        ' Adicionar o PlotView ao painel
        panel.Controls.Add(plotView)

        ' Adicionar o painel à segunda linha do TableLayoutPanel
        tableLayout.Controls.Add(panel, 0, 1)
    End Sub

    Private Sub SairToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles SairToolStripMenuItem.Click
        Application.Exit()
    End Sub

    Private Sub GraficoEmpresasToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles GraficoEmpresasToolStripMenuItem.Click
        Dim frm As New Grafico_Empresas()

        frm.Show()
        Me.Hide()
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

    Private Sub DadosToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles DadosToolStripMenuItem.Click

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
