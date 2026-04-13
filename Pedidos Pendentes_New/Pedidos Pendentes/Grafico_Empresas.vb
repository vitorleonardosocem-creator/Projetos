Imports System.Data.SqlClient
Imports Microsoft.Data.SqlClient
Imports OxyPlot
Imports OxyPlot.Axes
Imports OxyPlot.Series
Imports OxyPlot.WindowsForms

Public Class Grafico_Empresas

    Private Sub Graficos_Load(sender As Object, e As EventArgs) Handles MyBase.Load
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
        tableLayout.Controls.Add(MenuStrip2, 0, 0)

        ' Criar o modelo de gráfico
        Dim plotModel As New PlotModel() With {
            .Title = "Número de Visitantes por Empresa"
        }

        ' Criar a série de barras
        Dim barSeries As New BarSeries() With {
            .Title = "Visitantes",
            .StrokeThickness = 1,
            .FillColor = OxyColor.FromRgb(0, 128, 255)
        }

        ' Definir a string de conexão (ajuste para o seu banco de dados)
        Dim connectionString As String = "Server=192.168.10.156;Database=Visitantes;User Id=GV;Password=NovaSenhaForte987;TrustServerCertificate=True;"

        ' Consultar os dados do banco de dados para contar o número de visitantes por empresa
        Dim query As String = "SELECT Empresa, COUNT(Id) AS TotalVisitantes FROM Visitantes GROUP BY Empresa"

        ' Usar SqlConnection e SqlCommand para obter os dados
        Using conn As New SqlConnection(connectionString)
            Using cmd As New SqlCommand(query, conn)
                conn.Open()

                ' Ler os dados e adicionar ao gráfico
                Using reader As SqlDataReader = cmd.ExecuteReader()
                    While reader.Read()
                        Dim empresa As String = reader("Empresa").ToString()
                        Dim totalVisitantes As Integer = Convert.ToInt32(reader("TotalVisitantes"))

                        ' Adicionar os dados à série de barras
                        barSeries.Items.Add(New BarItem() With {.Value = totalVisitantes})
                    End While
                End Using
            End Using
        End Using

        ' Configurar o eixo Y (categoria) com os nomes das empresas
        Dim categoryAxis As New CategoryAxis() With {
            .Position = AxisPosition.Left ' Eixo Y (vertical)
        }

        ' Reconsultar os dados para pegar os nomes das empresas
        Using conn As New SqlConnection(connectionString)
            Using cmd As New SqlCommand(query, conn)
                conn.Open()

                ' Adicionar os nomes das empresas ao eixo Y (vertical)
                Using reader As SqlDataReader = cmd.ExecuteReader()
                    While reader.Read()
                        Dim empresa As String = reader("Empresa").ToString()
                        categoryAxis.Labels.Add(empresa)
                    End While
                End Using
            End Using
        End Using

        ' Adicionar o eixo Y (vertical) ao gráfico
        plotModel.Axes.Add(categoryAxis)

        ' Configurar o eixo X (numérico) para mostrar os valores de "TotalVisitantes"
        Dim linearAxis As New LinearAxis() With {
            .Position = AxisPosition.Bottom, ' Eixo X (horizontal)
            .Title = "Número de Visitantes",
            .MajorStep = 1, ' Passo maior de 1 para garantir números inteiros
            .MinorStep = 1, ' Passo menor também de 1
            .StringFormat = "0" ' Mostrar números inteiros (sem casas decimais)
        }

        ' Adicionar o eixo X ao gráfico
        plotModel.Axes.Add(linearAxis)

        ' Adicionar a série de barras ao gráfico
        plotModel.Series.Add(barSeries)

        ' Criar o controle PlotView para exibir o gráfico
        Dim plotView As New PlotView() With {
            .Model = plotModel,
            .Dock = DockStyle.Fill ' O gráfico vai preencher o restante da segunda linha
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

    Private Sub SairToolStripMenuItem_Click(sender As Object, e As EventArgs)
        Application.Exit
    End Sub

    Private Sub ListaToolStripMenuItem_Click(sender As Object, e As EventArgs)
        Dim frm As New ListaVisitantes

        frm.Show
        Close
    End Sub

    Private Sub ArovarOuRejeitarToolStripMenuItem_Click(sender As Object, e As EventArgs)
        Dim frm As New Aprovacao

        frm.Show
        Close
    End Sub

    Private Sub IrParaOMenuToolStripMenuItem_Click(sender As Object, e As EventArgs)
        Dim frm As New Menu

        frm.Show
        Close
    End Sub

    Private Sub GraficoTotalVisitantesToolStripMenuItem_Click(sender As Object, e As EventArgs)
        Dim frm As New Grafico_Total_Visitantes

        frm.Show
        Hide
    End Sub

    Private Sub ListaComFotoToolStripMenuItem_Click(sender As Object, e As EventArgs)
        Dim frm As New Lista_Individual

        frm.Show
        Close
    End Sub

    Private Sub ClientesToolStripMenuItem_Click(sender As Object, e As EventArgs)
        Dim frm As New InserirVisitantes

        frm.Show
        Close
    End Sub

    Private Sub ClientesToolStripMenuItem1_Click(sender As Object, e As EventArgs)
        Dim frm As New Clientes

        frm.Show
        Close
    End Sub

    Private Sub ListaDeClientesToolStripMenuItem_Click(sender As Object, e As EventArgs)
        Dim frm As New ListaClientes

        frm.Show
        Close
    End Sub

    Private Sub ToolStripMenuItem13_Click(sender As Object, e As EventArgs) Handles ToolStripMenuItem13.Click
        Dim frm As New Menu()

        frm.Show()
        Me.Close()
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

    Private Sub ToolStripMenuItem11_Click(sender As Object, e As EventArgs) Handles ToolStripMenuItem11.Click
        Dim frm As New Clientes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub InserirClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles InserirClientesToolStripMenuItem.Click
        Dim frm As New ListaClientes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ToolStripMenuItem8_Click(sender As Object, e As EventArgs) Handles ToolStripMenuItem8.Click
        Dim frm As New InserirVisitantes()
        frm.Show()
        Me.Close()
    End Sub

    Private Sub ToolStripMenuItem9_Click(sender As Object, e As EventArgs) Handles ToolStripMenuItem9.Click
        Dim frm As New InserirVisitantesFornecedores()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ToolStripMenuItem5_Click(sender As Object, e As EventArgs) Handles ToolStripMenuItem5.Click
        Dim frm As New ListaVisitantes()
        frm.Show()
        Me.Hide()
    End Sub

    Private Sub ToolStripMenuItem6_Click(sender As Object, e As EventArgs) Handles ToolStripMenuItem6.Click
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
