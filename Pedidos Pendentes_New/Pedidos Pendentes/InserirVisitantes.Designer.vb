<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class InserirVisitantes
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
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(InserirVisitantes))
        Label7 = New Label()
        Label5 = New Label()
        Label4 = New Label()
        Label3 = New Label()
        Label2 = New Label()
        txtEmail = New TextBox()
        txtTelefone = New TextBox()
        txtEmpresa = New TextBox()
        txtNome = New TextBox()
        btnGravar = New Button()
        lblDataFim = New Label()
        Date2 = New DateTimePicker()
        chkMultiplosDias = New CheckBox()
        MenuStrip1 = New MenuStrip()
        FicheiroToolStripMenuItem = New ToolStripMenuItem()
        SairToolStripMenuItem = New ToolStripMenuItem()
        DashboardToolStripMenuItem = New ToolStripMenuItem()
        GraficoEmpresasToolStripMenuItem = New ToolStripMenuItem()
        GraficoTotalVisitantesToolStripMenuItem = New ToolStripMenuItem()
        VisitantesToolStripMenuItem = New ToolStripMenuItem()
        ListaToolStripMenuItem = New ToolStripMenuItem()
        ListaComFotoToolStripMenuItem = New ToolStripMenuItem()
        ListaDeVisitantesFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        DadosToolStripMenuItem = New ToolStripMenuItem()
        ClientesToolStripMenuItem = New ToolStripMenuItem()
        VisitasFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        ClientesToolStripMenuItem1 = New ToolStripMenuItem()
        InserirClientesToolStripMenuItem = New ToolStripMenuItem()
        ListaDeClientesToolStripMenuItem = New ToolStripMenuItem()
        FornecedoresToolStripMenuItem = New ToolStripMenuItem()
        InserirFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        ListaDeFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        MenuToolStripMenuItem = New ToolStripMenuItem()
        IrParaOMenuToolStripMenuItem = New ToolStripMenuItem()
        PedidosPendentesToolStripMenuItem = New ToolStripMenuItem()
        ArovarOuRejeitarToolStripMenuItem = New ToolStripMenuItem()
        Label1 = New Label()
        Label6 = New Label()
        txtObservacao = New TextBox()
        Date1 = New DateTimePicker()
        chkAlmoco = New CheckBox()
        ComboBoxResponsavel = New ComboBox()
        MenuStrip1.SuspendLayout()
        SuspendLayout()
        ' 
        ' Label7
        ' 
        Label7.AutoSize = True
        Label7.BackColor = Color.Transparent
        Label7.ForeColor = Color.DeepSkyBlue
        Label7.Location = New Point(808, 131)
        Label7.Margin = New Padding(4, 0, 4, 0)
        Label7.Name = "Label7"
        Label7.Size = New Size(85, 23)
        Label7.TabIndex = 30
        Label7.Text = "Data Início:"
        ' 
        ' Label5
        ' 
        Label5.AutoSize = True
        Label5.BackColor = Color.Transparent
        Label5.ForeColor = Color.DeepSkyBlue
        Label5.Location = New Point(248, 441)
        Label5.Margin = New Padding(4, 0, 4, 0)
        Label5.Name = "Label5"
        Label5.Size = New Size(48, 23)
        Label5.TabIndex = 28
        Label5.Text = "Email"
        ' 
        ' Label4
        ' 
        Label4.AutoSize = True
        Label4.BackColor = Color.Transparent
        Label4.ForeColor = Color.DeepSkyBlue
        Label4.Location = New Point(248, 334)
        Label4.Margin = New Padding(4, 0, 4, 0)
        Label4.Name = "Label4"
        Label4.Size = New Size(70, 23)
        Label4.TabIndex = 27
        Label4.Text = "Telefone"
        ' 
        ' Label3
        ' 
        Label3.AutoSize = True
        Label3.BackColor = Color.Transparent
        Label3.ForeColor = Color.DeepSkyBlue
        Label3.Location = New Point(248, 237)
        Label3.Margin = New Padding(4, 0, 4, 0)
        Label3.Name = "Label3"
        Label3.Size = New Size(73, 23)
        Label3.TabIndex = 26
        Label3.Text = "Empresa"
        ' 
        ' Label2
        ' 
        Label2.AutoSize = True
        Label2.BackColor = Color.Transparent
        Label2.Font = New Font("Arial Narrow", 14.25F, FontStyle.Bold, GraphicsUnit.Point, CByte(0))
        Label2.ForeColor = Color.DeepSkyBlue
        Label2.Location = New Point(248, 131)
        Label2.Margin = New Padding(4, 0, 4, 0)
        Label2.Name = "Label2"
        Label2.Size = New Size(54, 23)
        Label2.TabIndex = 25
        Label2.Text = "Nome"
        ' 
        ' txtEmail
        ' 
        txtEmail.BackColor = SystemColors.ScrollBar
        txtEmail.Location = New Point(248, 484)
        txtEmail.Margin = New Padding(4, 5, 4, 5)
        txtEmail.Name = "txtEmail"
        txtEmail.Size = New Size(382, 29)
        txtEmail.TabIndex = 21
        ' 
        ' txtTelefone
        ' 
        txtTelefone.BackColor = SystemColors.ScrollBar
        txtTelefone.Location = New Point(248, 379)
        txtTelefone.Margin = New Padding(4, 5, 4, 5)
        txtTelefone.Name = "txtTelefone"
        txtTelefone.Size = New Size(382, 29)
        txtTelefone.TabIndex = 20
        ' 
        ' txtEmpresa
        ' 
        txtEmpresa.BackColor = SystemColors.ScrollBar
        txtEmpresa.Location = New Point(248, 279)
        txtEmpresa.Margin = New Padding(4, 5, 4, 5)
        txtEmpresa.Name = "txtEmpresa"
        txtEmpresa.Size = New Size(382, 29)
        txtEmpresa.TabIndex = 19
        ' 
        ' txtNome
        ' 
        txtNome.BackColor = SystemColors.ScrollBar
        txtNome.Location = New Point(248, 178)
        txtNome.Margin = New Padding(4, 5, 4, 5)
        txtNome.Name = "txtNome"
        txtNome.Size = New Size(382, 29)
        txtNome.TabIndex = 18
        ' 
        ' btnGravar
        ' 
        btnGravar.BackColor = Color.DeepSkyBlue
        btnGravar.ForeColor = SystemColors.ControlLightLight
        btnGravar.Location = New Point(1102, 568)
        btnGravar.Margin = New Padding(4, 5, 4, 5)
        btnGravar.Name = "btnGravar"
        btnGravar.Size = New Size(88, 38)
        btnGravar.TabIndex = 25
        btnGravar.Text = "Gravar"
        btnGravar.UseVisualStyleBackColor = False
        ' 
        ' lblDataFim
        ' 
        lblDataFim.AutoSize = True
        lblDataFim.BackColor = Color.Transparent
        lblDataFim.Enabled = False
        lblDataFim.ForeColor = Color.DeepSkyBlue
        lblDataFim.Location = New Point(1025, 131)
        lblDataFim.Name = "lblDataFim"
        lblDataFim.Size = New Size(76, 23)
        lblDataFim.TabIndex = 39
        lblDataFim.Text = "Data Fim:"
        ' 
        ' Date2
        ' 
        Date2.Enabled = False
        Date2.Location = New Point(1025, 176)
        Date2.Name = "Date2"
        Date2.Size = New Size(200, 29)
        Date2.TabIndex = 40
        ' 
        ' chkMultiplosDias
        ' 
        chkMultiplosDias.AutoSize = True
        chkMultiplosDias.BackColor = SystemColors.GradientActiveCaption
        chkMultiplosDias.Location = New Point(1240, 176)
        chkMultiplosDias.Name = "chkMultiplosDias"
        chkMultiplosDias.Size = New Size(144, 27)
        chkMultiplosDias.TabIndex = 41
        chkMultiplosDias.Text = "Mais de um dia?"
        chkMultiplosDias.UseVisualStyleBackColor = False
        ' 
        ' MenuStrip1
        ' 
        MenuStrip1.Items.AddRange(New ToolStripItem() {FicheiroToolStripMenuItem, DashboardToolStripMenuItem, VisitantesToolStripMenuItem, DadosToolStripMenuItem, ClientesToolStripMenuItem1, FornecedoresToolStripMenuItem, MenuToolStripMenuItem, PedidosPendentesToolStripMenuItem})
        MenuStrip1.Location = New Point(0, 0)
        MenuStrip1.Name = "MenuStrip1"
        MenuStrip1.Padding = New Padding(8, 3, 0, 3)
        MenuStrip1.Size = New Size(1402, 25)
        MenuStrip1.TabIndex = 34
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
        DashboardToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {GraficoEmpresasToolStripMenuItem, GraficoTotalVisitantesToolStripMenuItem})
        DashboardToolStripMenuItem.Name = "DashboardToolStripMenuItem"
        DashboardToolStripMenuItem.Size = New Size(76, 19)
        DashboardToolStripMenuItem.Text = "Dashboard"
        ' 
        ' GraficoEmpresasToolStripMenuItem
        ' 
        GraficoEmpresasToolStripMenuItem.Name = "GraficoEmpresasToolStripMenuItem"
        GraficoEmpresasToolStripMenuItem.Size = New Size(194, 22)
        GraficoEmpresasToolStripMenuItem.Text = "Grafico Empresas"
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
        ' DadosToolStripMenuItem
        ' 
        DadosToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {ClientesToolStripMenuItem, VisitasFornecedoresToolStripMenuItem})
        DadosToolStripMenuItem.Name = "DadosToolStripMenuItem"
        DadosToolStripMenuItem.Size = New Size(52, 19)
        DadosToolStripMenuItem.Text = "Visitas"
        ' 
        ' ClientesToolStripMenuItem
        ' 
        ClientesToolStripMenuItem.Name = "ClientesToolStripMenuItem"
        ClientesToolStripMenuItem.Size = New Size(181, 22)
        ClientesToolStripMenuItem.Text = "Visitas Clientes"
        ' 
        ' VisitasFornecedoresToolStripMenuItem
        ' 
        VisitasFornecedoresToolStripMenuItem.Name = "VisitasFornecedoresToolStripMenuItem"
        VisitasFornecedoresToolStripMenuItem.Size = New Size(181, 22)
        VisitasFornecedoresToolStripMenuItem.Text = "Visitas Fornecedores"
        ' 
        ' ClientesToolStripMenuItem1
        ' 
        ClientesToolStripMenuItem1.DropDownItems.AddRange(New ToolStripItem() {InserirClientesToolStripMenuItem, ListaDeClientesToolStripMenuItem})
        ClientesToolStripMenuItem1.Name = "ClientesToolStripMenuItem1"
        ClientesToolStripMenuItem1.Size = New Size(61, 19)
        ClientesToolStripMenuItem1.Text = "Clientes"
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
        ' Label1
        ' 
        Label1.AutoSize = True
        Label1.BackColor = Color.Transparent
        Label1.ForeColor = Color.DeepSkyBlue
        Label1.Location = New Point(808, 237)
        Label1.Margin = New Padding(4, 0, 4, 0)
        Label1.Name = "Label1"
        Label1.Size = New Size(101, 23)
        Label1.TabIndex = 35
        Label1.Text = "Responsável"
        ' 
        ' Label6
        ' 
        Label6.AutoSize = True
        Label6.BackColor = Color.Transparent
        Label6.ForeColor = Color.DeepSkyBlue
        Label6.Location = New Point(808, 334)
        Label6.Margin = New Padding(4, 0, 4, 0)
        Label6.Name = "Label6"
        Label6.Size = New Size(95, 23)
        Label6.TabIndex = 36
        Label6.Text = "Observação"
        ' 
        ' txtObservacao
        ' 
        txtObservacao.BackColor = SystemColors.ScrollBar
        txtObservacao.Location = New Point(808, 379)
        txtObservacao.Margin = New Padding(4, 5, 4, 5)
        txtObservacao.Multiline = True
        txtObservacao.Name = "txtObservacao"
        txtObservacao.Size = New Size(382, 106)
        txtObservacao.TabIndex = 24
        ' 
        ' Date1
        ' 
        Date1.Location = New Point(808, 176)
        Date1.Name = "Date1"
        Date1.Size = New Size(200, 29)
        Date1.TabIndex = 22
        ' 
        ' chkAlmoco
        ' 
        chkAlmoco.AutoSize = True
        chkAlmoco.BackColor = SystemColors.GradientActiveCaption
        chkAlmoco.Location = New Point(808, 506)
        chkAlmoco.Name = "chkAlmoco"
        chkAlmoco.Size = New Size(81, 27)
        chkAlmoco.TabIndex = 37
        chkAlmoco.Text = "Almoço"
        chkAlmoco.UseVisualStyleBackColor = False
        ' 
        ' ComboBoxResponsavel
        ' 
        ComboBoxResponsavel.DropDownStyle = ComboBoxStyle.DropDownList
        ComboBoxResponsavel.FormattingEnabled = True
        ComboBoxResponsavel.Items.AddRange(New Object() {"Carlos Balata", "Emilio Vigia", "Fernando Xavier", "Filipe Loureiro", "Joao Monteiro", "Micael Dias", "Pedro Bonifacio", "Rui Novo", "Veronica Rosa", "Virginia Lopes", "Monica Vicente", "Pedro Vicente", "Telmo Febra", "Henrique Carvalho", "Joao Bernardino", "Centro Ensaios", "Commercial Team", "IT", "Manutencao", "Fabricacao", "Qualidade", "Compras", "Logistica"})
        ComboBoxResponsavel.Location = New Point(808, 277)
        ComboBoxResponsavel.Name = "ComboBoxResponsavel"
        ComboBoxResponsavel.Size = New Size(382, 31)
        ComboBoxResponsavel.TabIndex = 38
        ' 
        ' InserirVisitantes
        ' 
        AutoScaleDimensions = New SizeF(9F, 23F)
        AutoScaleMode = AutoScaleMode.Font
        BackColor = SystemColors.AppWorkspace
        BackgroundImage = CType(resources.GetObject("$this.BackgroundImage"), Image)
        BackgroundImageLayout = ImageLayout.Stretch
        ClientSize = New Size(1402, 629)
        Controls.Add(ComboBoxResponsavel)
        Controls.Add(chkAlmoco)
        Controls.Add(chkMultiplosDias)
        Controls.Add(Date2)
        Controls.Add(lblDataFim)
        Controls.Add(Date1)
        Controls.Add(txtObservacao)
        Controls.Add(Label6)
        Controls.Add(Label1)
        Controls.Add(btnGravar)
        Controls.Add(Label7)
        Controls.Add(Label5)
        Controls.Add(Label4)
        Controls.Add(Label3)
        Controls.Add(Label2)
        Controls.Add(txtEmail)
        Controls.Add(txtTelefone)
        Controls.Add(txtEmpresa)
        Controls.Add(txtNome)
        Controls.Add(MenuStrip1)
        Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        MainMenuStrip = MenuStrip1
        Margin = New Padding(4, 5, 4, 5)
        Name = "InserirVisitantes"
        StartPosition = FormStartPosition.CenterScreen
        Text = "InserirVisitantes"
        MenuStrip1.ResumeLayout(False)
        MenuStrip1.PerformLayout()
        ResumeLayout(False)
        PerformLayout()
    End Sub
    Friend WithEvents Label7 As Label
    Friend WithEvents Label5 As Label
    Friend WithEvents Label4 As Label
    Friend WithEvents Label3 As Label
    Friend WithEvents Label2 As Label
    Friend WithEvents txtEmail As TextBox
    Friend WithEvents txtTelefone As TextBox
    Friend WithEvents txtEmpresa As TextBox
    Friend WithEvents txtNome As TextBox
    Friend WithEvents btnGravar As Button
    Friend WithEvents MenuStrip1 As MenuStrip
    Friend WithEvents FicheiroToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents SairToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents DashboardToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficoEmpresasToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficoTotalVisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents VisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaComFotoToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents PedidosPendentesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ArovarOuRejeitarToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents MenuToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents IrParaOMenuToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents Label1 As Label
    Friend WithEvents Label6 As Label
    Friend WithEvents txtObservacao As TextBox
    Friend WithEvents Date1 As DateTimePicker
    Friend WithEvents chkAlmoco As CheckBox
    Friend WithEvents DadosToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ClientesToolStripMenuItem1 As ToolStripMenuItem
    Friend WithEvents ListaDeClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents FornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents InserirFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents InserirClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents VisitasFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeVisitantesFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ComboBoxResponsavel As ComboBox
    Friend WithEvents lblDataFim As Label
    Friend WithEvents Date2 As DateTimePicker
    Friend WithEvents chkMultiplosDias As CheckBox
End Class
