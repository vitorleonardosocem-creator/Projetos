<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Fornecedores
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
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(Fornecedores))
        btnGravar = New Button()
        Label5 = New Label()
        Label4 = New Label()
        Label3 = New Label()
        Label2 = New Label()
        txtEmail = New TextBox()
        txtTelefone = New TextBox()
        txtEmpresa = New TextBox()
        txtNome = New TextBox()
        MenuStrip2 = New MenuStrip()
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
        VisitasFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        ClientesToolStripMenuItem = New ToolStripMenuItem()
        InserirClientesToolStripMenuItem = New ToolStripMenuItem()
        ListaDeClientesToolStripMenuItem = New ToolStripMenuItem()
        FornecedoresToolStripMenuItem = New ToolStripMenuItem()
        InserirFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        ListaDeFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        MenuToolStripMenuItem = New ToolStripMenuItem()
        IrParaOMenuToolStripMenuItem = New ToolStripMenuItem()
        PedidosPendentesToolStripMenuItem = New ToolStripMenuItem()
        ArovarOuRejeitarToolStripMenuItem = New ToolStripMenuItem()
        MenuStrip2.SuspendLayout()
        SuspendLayout()
        ' 
        ' btnGravar
        ' 
        btnGravar.Location = New Point(1146, 281)
        btnGravar.Name = "btnGravar"
        btnGravar.Size = New Size(99, 44)
        btnGravar.TabIndex = 46
        btnGravar.Text = "Gravar"
        btnGravar.UseVisualStyleBackColor = True
        ' 
        ' Label5
        ' 
        Label5.AutoSize = True
        Label5.BackColor = Color.Transparent
        Label5.Font = New Font("Arial Narrow", 14.25F)
        Label5.ForeColor = Color.DeepSkyBlue
        Label5.Location = New Point(586, 396)
        Label5.Margin = New Padding(4, 0, 4, 0)
        Label5.Name = "Label5"
        Label5.Size = New Size(48, 23)
        Label5.TabIndex = 45
        Label5.Text = "Email"
        ' 
        ' Label4
        ' 
        Label4.AutoSize = True
        Label4.BackColor = Color.Transparent
        Label4.Font = New Font("Arial Narrow", 14.25F)
        Label4.ForeColor = Color.DeepSkyBlue
        Label4.Location = New Point(586, 289)
        Label4.Margin = New Padding(4, 0, 4, 0)
        Label4.Name = "Label4"
        Label4.Size = New Size(70, 23)
        Label4.TabIndex = 44
        Label4.Text = "Telefone"
        ' 
        ' Label3
        ' 
        Label3.AutoSize = True
        Label3.BackColor = Color.Transparent
        Label3.Font = New Font("Arial Narrow", 14.25F)
        Label3.ForeColor = Color.DeepSkyBlue
        Label3.Location = New Point(586, 192)
        Label3.Margin = New Padding(4, 0, 4, 0)
        Label3.Name = "Label3"
        Label3.Size = New Size(73, 23)
        Label3.TabIndex = 43
        Label3.Text = "Empresa"
        ' 
        ' Label2
        ' 
        Label2.AutoSize = True
        Label2.BackColor = Color.Transparent
        Label2.Font = New Font("Arial Narrow", 14.25F)
        Label2.ForeColor = Color.DeepSkyBlue
        Label2.Location = New Point(586, 92)
        Label2.Margin = New Padding(4, 0, 4, 0)
        Label2.Name = "Label2"
        Label2.Size = New Size(52, 23)
        Label2.TabIndex = 42
        Label2.Text = "Nome"
        ' 
        ' txtEmail
        ' 
        txtEmail.BackColor = SystemColors.ScrollBar
        txtEmail.Location = New Point(586, 439)
        txtEmail.Margin = New Padding(4, 5, 4, 5)
        txtEmail.Name = "txtEmail"
        txtEmail.Size = New Size(382, 23)
        txtEmail.TabIndex = 41
        ' 
        ' txtTelefone
        ' 
        txtTelefone.BackColor = SystemColors.ScrollBar
        txtTelefone.Location = New Point(586, 334)
        txtTelefone.Margin = New Padding(4, 5, 4, 5)
        txtTelefone.Name = "txtTelefone"
        txtTelefone.Size = New Size(382, 23)
        txtTelefone.TabIndex = 40
        ' 
        ' txtEmpresa
        ' 
        txtEmpresa.BackColor = SystemColors.ScrollBar
        txtEmpresa.Location = New Point(586, 234)
        txtEmpresa.Margin = New Padding(4, 5, 4, 5)
        txtEmpresa.Name = "txtEmpresa"
        txtEmpresa.Size = New Size(382, 23)
        txtEmpresa.TabIndex = 39
        ' 
        ' txtNome
        ' 
        txtNome.BackColor = SystemColors.ScrollBar
        txtNome.Location = New Point(586, 133)
        txtNome.Margin = New Padding(4, 5, 4, 5)
        txtNome.Name = "txtNome"
        txtNome.Size = New Size(382, 23)
        txtNome.TabIndex = 38
        ' 
        ' MenuStrip2
        ' 
        MenuStrip2.Items.AddRange(New ToolStripItem() {FicheiroToolStripMenuItem, DashboardToolStripMenuItem, VisitantesToolStripMenuItem, TesteToolStripMenuItem, ClientesToolStripMenuItem, FornecedoresToolStripMenuItem, MenuToolStripMenuItem, PedidosPendentesToolStripMenuItem})
        MenuStrip2.Location = New Point(0, 0)
        MenuStrip2.Name = "MenuStrip2"
        MenuStrip2.Padding = New Padding(7, 3, 0, 3)
        MenuStrip2.Size = New Size(1464, 25)
        MenuStrip2.TabIndex = 47
        MenuStrip2.Text = "MenuStrip2"
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
        ListaToolStripMenuItem.Size = New Size(240, 22)
        ListaToolStripMenuItem.Text = "Lista de visitantes Clientes"
        ' 
        ' ListaComFotoToolStripMenuItem
        ' 
        ListaComFotoToolStripMenuItem.Name = "ListaComFotoToolStripMenuItem"
        ListaComFotoToolStripMenuItem.Size = New Size(240, 22)
        ListaComFotoToolStripMenuItem.Text = "Lista de visitantes Individual"
        ' 
        ' ListaDeVisitantesFornecedoresToolStripMenuItem
        ' 
        ListaDeVisitantesFornecedoresToolStripMenuItem.Name = "ListaDeVisitantesFornecedoresToolStripMenuItem"
        ListaDeVisitantesFornecedoresToolStripMenuItem.Size = New Size(240, 22)
        ListaDeVisitantesFornecedoresToolStripMenuItem.Text = "Lista de visitantes Fornecedores"
        ' 
        ' TesteToolStripMenuItem
        ' 
        TesteToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {TEsteToolStripMenuItem1, VisitasFornecedoresToolStripMenuItem})
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
        ' VisitasFornecedoresToolStripMenuItem
        ' 
        VisitasFornecedoresToolStripMenuItem.Name = "VisitasFornecedoresToolStripMenuItem"
        VisitasFornecedoresToolStripMenuItem.Size = New Size(181, 22)
        VisitasFornecedoresToolStripMenuItem.Text = "Visitas Fornecedores"
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
        ' MenuToolStripMenuItem
        ' 
        MenuToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {IrParaOMenuToolStripMenuItem})
        MenuToolStripMenuItem.Name = "MenuToolStripMenuItem"
        MenuToolStripMenuItem.Size = New Size(50, 19)
        MenuToolStripMenuItem.Text = "Menu"
        ' 
        ' IrParaOMenuToolStripMenuItem
        ' 
        IrParaOMenuToolStripMenuItem.Name = "IrParaOMenuToolStripMenuItem"
        IrParaOMenuToolStripMenuItem.Size = New Size(151, 22)
        IrParaOMenuToolStripMenuItem.Text = "Ir para o Menu"
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
        ' Fornecedores
        ' 
        AutoScaleDimensions = New SizeF(7F, 15F)
        AutoScaleMode = AutoScaleMode.Font
        BackgroundImage = CType(resources.GetObject("$this.BackgroundImage"), Image)
        BackgroundImageLayout = ImageLayout.Stretch
        ClientSize = New Size(1464, 529)
        Controls.Add(MenuStrip2)
        Controls.Add(btnGravar)
        Controls.Add(Label5)
        Controls.Add(Label4)
        Controls.Add(Label3)
        Controls.Add(Label2)
        Controls.Add(txtEmail)
        Controls.Add(txtTelefone)
        Controls.Add(txtEmpresa)
        Controls.Add(txtNome)
        Name = "Fornecedores"
        Text = "Fornecedores"
        MenuStrip2.ResumeLayout(False)
        MenuStrip2.PerformLayout()
        ResumeLayout(False)
        PerformLayout()
    End Sub
    Friend WithEvents btnGravar As Button
    Friend WithEvents Label5 As Label
    Friend WithEvents Label4 As Label
    Friend WithEvents Label3 As Label
    Friend WithEvents Label2 As Label
    Friend WithEvents txtEmail As TextBox
    Friend WithEvents txtTelefone As TextBox
    Friend WithEvents txtEmpresa As TextBox
    Friend WithEvents txtNome As TextBox
    Friend WithEvents MenuStrip2 As MenuStrip
    Friend WithEvents FicheiroToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents SairToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents DashboardToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficosToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficoTotalVisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents VisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaComFotoToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents TesteToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents TEsteToolStripMenuItem1 As ToolStripMenuItem
    Friend WithEvents ClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents MenuToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents IrParaOMenuToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents PedidosPendentesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ArovarOuRejeitarToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents FornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents InserirFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents InserirClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents VisitasFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeVisitantesFornecedoresToolStripMenuItem As ToolStripMenuItem
End Class
