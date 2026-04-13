Public Class Menu
    Private Sub Menu_Load(sender As Object, e As EventArgs) Handles MyBase.Load

    End Sub

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
        Me.Hide()
    End Sub

    Private Sub TEsteToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles TEsteToolStripMenuItem1.Click
        Dim frm As New InserirVisitantes()

        frm.Show()

    End Sub

    Private Sub ToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles ToolStripMenuItem1.Click
        Dim frm As New InserirVisitantesFornecedores()

        frm.Show()
    End Sub

    Private Sub ListaDeClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeClientesToolStripMenuItem.Click
        Dim frm As New ListaClientes()

        frm.Show()
    End Sub

    Private Sub InserirClientesToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles InserirClientesToolStripMenuItem.Click
        Dim frm As New Clientes()

        frm.Show()
    End Sub

    Private Sub InserirFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles InserirFornecedoresToolStripMenuItem.Click
        Dim frm As New Fornecedores()

        frm.Show()
    End Sub

    Private Sub ListaDeFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeFornecedoresToolStripMenuItem.Click
        Dim frm As New ListaFornecedores()

        frm.Show()
    End Sub

    Private Sub ListaDeVisitantesFornecedoresToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ListaDeVisitantesFornecedoresToolStripMenuItem.Click
        Dim frm As New ListaVisitantesFornecedores()

        frm.Show()
        Me.Hide()
    End Sub
End Class