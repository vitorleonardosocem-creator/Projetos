<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Menu
    Inherits System.Windows.Forms.Form

    'Descartar substituições de formulário para limpar a lista de componentes.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Exigido pelo Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'OBSERVAÇÃO: o procedimento a seguir é exigido pelo Windows Form Designer
    'Pode ser modificado usando o Windows Form Designer.  
    'Não o modifique usando o editor de códigos.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(Menu))
        MenuStrip1 = New MenuStrip()
        FicheiroToolStripMenuItem = New ToolStripMenuItem()
        SairToolStripMenuItem = New ToolStripMenuItem()
        DashboardToolStripMenuItem = New ToolStripMenuItem()
        GraficosToolStripMenuItem = New ToolStripMenuItem()
        GraficoTotalVisitantesToolStripMenuItem = New ToolStripMenuItem()
        VisitantesToolStripMenuItem = New ToolStripMenuItem()
        ListaToolStripMenuItem = New ToolStripMenuItem()
        ListaComFotoToolStripMenuItem = New ToolStripMenuItem()
        ListaDeVisitantesFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        TesteToolStripMenuItem = New ToolStripMenuItem()
        TEsteToolStripMenuItem1 = New ToolStripMenuItem()
        ToolStripMenuItem1 = New ToolStripMenuItem()
        ClientesToolStripMenuItem = New ToolStripMenuItem()
        InserirClientesToolStripMenuItem = New ToolStripMenuItem()
        ListaDeClientesToolStripMenuItem = New ToolStripMenuItem()
        FornecedoresToolStripMenuItem = New ToolStripMenuItem()
        InserirFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        ListaDeFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        PedidosPendentesToolStripMenuItem = New ToolStripMenuItem()
        ArovarOuRejeitarToolStripMenuItem = New ToolStripMenuItem()
        MenuStrip1.SuspendLayout()
        SuspendLayout()
        ' 
        ' MenuStrip1
        ' 
        MenuStrip1.Items.AddRange(New ToolStripItem() {FicheiroToolStripMenuItem, DashboardToolStripMenuItem, VisitantesToolStripMenuItem, TesteToolStripMenuItem, ClientesToolStripMenuItem, FornecedoresToolStripMenuItem, PedidosPendentesToolStripMenuItem})
        MenuStrip1.Location = New Point(0, 0)
        MenuStrip1.Name = "MenuStrip1"
        MenuStrip1.Padding = New Padding(7, 3, 0, 3)
        MenuStrip1.Size = New Size(1168, 25)
        MenuStrip1.TabIndex = 0
        MenuStrip1.Text = "MenuStrip1"
        ' 
        ' FicheiroToolStripMenuItem
        ' 
        FicheiroToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {SairToolStripMenuItem})
        FicheiroToolStripMenuItem.Name = "FicheiroToolStripMenuItem"
        FicheiroToolStripMenuItem.Size = New Size(61, 19)
        FicheiroToolStripMenuItem.Text = "Ficheiro"
        ' 
        ' SairToolStripMenuItem
        ' 
        SairToolStripMenuItem.Name = "SairToolStripMenuItem"
        SairToolStripMenuItem.Size = New Size(93, 22)
        SairToolStripMenuItem.Text = "Sair"
        ' 
        ' DashboardToolStripMenuItem
        ' 
        DashboardToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {GraficosToolStripMenuItem, GraficoTotalVisitantesToolStripMenuItem})
        DashboardToolStripMenuItem.Name = "DashboardToolStripMenuItem"
        DashboardToolStripMenuItem.Size = New Size(76, 19)
        DashboardToolStripMenuItem.Text = "Dashboard"
        ' 
        ' GraficosToolStripMenuItem
        ' 
        GraficosToolStripMenuItem.Name = "GraficosToolStripMenuItem"
        GraficosToolStripMenuItem.Size = New Size(194, 22)
        GraficosToolStripMenuItem.Text = "Grafico Empresas"
        ' 
        ' GraficoTotalVisitantesToolStripMenuItem
        ' 
        GraficoTotalVisitantesToolStripMenuItem.Name = "GraficoTotalVisitantesToolStripMenuItem"
        GraficoTotalVisitantesToolStripMenuItem.Size = New Size(194, 22)
        GraficoTotalVisitantesToolStripMenuItem.Text = "Grafico Total Visitantes"
        ' 
        ' VisitantesToolStripMenuItem
        ' 
        VisitantesToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {ListaToolStripMenuItem, ListaComFotoToolStripMenuItem, ListaDeVisitantesFornecedoresToolStripMenuItem})
        VisitantesToolStripMenuItem.Name = "VisitantesToolStripMenuItem"
        VisitantesToolStripMenuItem.Size = New Size(112, 19)
        VisitantesToolStripMenuItem.Text = "Lista de Visitantes"
        ' 
        ' ListaToolStripMenuItem
        ' 
        ListaToolStripMenuItem.Name = "ListaToolStripMenuItem"
        ListaToolStripMenuItem.Size = New Size(269, 22)
        ListaToolStripMenuItem.Text = "Lista de visitantes Clientes"
        ' 
        ' ListaComFotoToolStripMenuItem
        ' 
        ListaComFotoToolStripMenuItem.Name = "ListaComFotoToolStripMenuItem"
        ListaComFotoToolStripMenuItem.Size = New Size(269, 22)
        ListaComFotoToolStripMenuItem.Text = "Lista de visitantes Clientes Individual "
        ' 
        ' ListaDeVisitantesFornecedoresToolStripMenuItem
        ' 
        ListaDeVisitantesFornecedoresToolStripMenuItem.Name = "ListaDeVisitantesFornecedoresToolStripMenuItem"
        ListaDeVisitantesFornecedoresToolStripMenuItem.Size = New Size(269, 22)
        ListaDeVisitantesFornecedoresToolStripMenuItem.Text = "Lista de visitantes Fornecedores"
        ' 
        ' TesteToolStripMenuItem
        ' 
        TesteToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {TEsteToolStripMenuItem1, ToolStripMenuItem1})
        TesteToolStripMenuItem.Name = "TesteToolStripMenuItem"
        TesteToolStripMenuItem.Size = New Size(52, 19)
        TesteToolStripMenuItem.Text = "Visitas"
        ' 
        ' TEsteToolStripMenuItem1
        ' 
        TEsteToolStripMenuItem1.Name = "TEsteToolStripMenuItem1"
        TEsteToolStripMenuItem1.Size = New Size(181, 22)
        TEsteToolStripMenuItem1.Text = "Visitas Clientes"
        ' 
        ' ToolStripMenuItem1
        ' 
        ToolStripMenuItem1.Name = "ToolStripMenuItem1"
        ToolStripMenuItem1.Size = New Size(181, 22)
        ToolStripMenuItem1.Text = "Visitas Fornecedores"
        ' 
        ' ClientesToolStripMenuItem
        ' 
        ClientesToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {InserirClientesToolStripMenuItem, ListaDeClientesToolStripMenuItem})
        ClientesToolStripMenuItem.Name = "ClientesToolStripMenuItem"
        ClientesToolStripMenuItem.Size = New Size(61, 19)
        ClientesToolStripMenuItem.Text = "Clientes"
        ' 
        ' InserirClientesToolStripMenuItem
        ' 
        InserirClientesToolStripMenuItem.Name = "InserirClientesToolStripMenuItem"
        InserirClientesToolStripMenuItem.Size = New Size(159, 22)
        InserirClientesToolStripMenuItem.Text = "Inserir Clientes"
        ' 
        ' ListaDeClientesToolStripMenuItem
        ' 
        ListaDeClientesToolStripMenuItem.Name = "ListaDeClientesToolStripMenuItem"
        ListaDeClientesToolStripMenuItem.Size = New Size(159, 22)
        ListaDeClientesToolStripMenuItem.Text = "Lista de Clientes"
        ' 
        ' FornecedoresToolStripMenuItem
        ' 
        FornecedoresToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {InserirFornecedoresToolStripMenuItem, ListaDeFornecedoresToolStripMenuItem})
        FornecedoresToolStripMenuItem.Name = "FornecedoresToolStripMenuItem"
        FornecedoresToolStripMenuItem.Size = New Size(90, 19)
        FornecedoresToolStripMenuItem.Text = "Fornecedores"
        ' 
        ' InserirFornecedoresToolStripMenuItem
        ' 
        InserirFornecedoresToolStripMenuItem.Name = "InserirFornecedoresToolStripMenuItem"
        InserirFornecedoresToolStripMenuItem.Size = New Size(188, 22)
        InserirFornecedoresToolStripMenuItem.Text = "Inserir Fornecedores"
        ' 
        ' ListaDeFornecedoresToolStripMenuItem
        ' 
        ListaDeFornecedoresToolStripMenuItem.Name = "ListaDeFornecedoresToolStripMenuItem"
        ListaDeFornecedoresToolStripMenuItem.Size = New Size(188, 22)
        ListaDeFornecedoresToolStripMenuItem.Text = "Lista de Fornecedores"
        ' 
        ' PedidosPendentesToolStripMenuItem
        ' 
        PedidosPendentesToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {ArovarOuRejeitarToolStripMenuItem})
        PedidosPendentesToolStripMenuItem.Enabled = False
        PedidosPendentesToolStripMenuItem.Name = "PedidosPendentesToolStripMenuItem"
        PedidosPendentesToolStripMenuItem.Size = New Size(119, 19)
        PedidosPendentesToolStripMenuItem.Text = "Pedidos Pendentes"
        ' 
        ' ArovarOuRejeitarToolStripMenuItem
        ' 
        ArovarOuRejeitarToolStripMenuItem.Name = "ArovarOuRejeitarToolStripMenuItem"
        ArovarOuRejeitarToolStripMenuItem.Size = New Size(168, 22)
        ArovarOuRejeitarToolStripMenuItem.Text = "Arovar ou Rejeitar"
        ' 
        ' Menu
        ' 
        AutoScaleDimensions = New SizeF(8F, 20F)
        AutoScaleMode = AutoScaleMode.Font
        BackColor = SystemColors.AppWorkspace
        BackgroundImage = CType(resources.GetObject("$this.BackgroundImage"), Image)
        BackgroundImageLayout = ImageLayout.Stretch
        ClientSize = New Size(1168, 637)
        Controls.Add(MenuStrip1)
        Font = New Font("Arial Narrow", 12F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        MainMenuStrip = MenuStrip1
        Margin = New Padding(3, 4, 3, 4)
        Name = "Menu"
        StartPosition = FormStartPosition.CenterScreen
        Text = "Menu"
        WindowState = FormWindowState.Maximized
        MenuStrip1.ResumeLayout(False)
        MenuStrip1.PerformLayout()
        ResumeLayout(False)
        PerformLayout()
    End Sub

    Friend WithEvents MenuStrip1 As MenuStrip
    Friend WithEvents FicheiroToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents SairToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents DashboardToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficosToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents VisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents PedidosPendentesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ArovarOuRejeitarToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficoTotalVisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaComFotoToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents TesteToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents TEsteToolStripMenuItem1 As ToolStripMenuItem
    Friend WithEvents ToolStripMenuItem1 As ToolStripMenuItem
    Friend WithEvents ClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents InserirClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents FornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents InserirFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeVisitantesFornecedoresToolStripMenuItem As ToolStripMenuItem
End Class
