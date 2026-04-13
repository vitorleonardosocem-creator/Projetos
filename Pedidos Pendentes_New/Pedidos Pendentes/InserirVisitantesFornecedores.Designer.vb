<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class InserirVisitantesFornecedores
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
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(InserirVisitantesFornecedores))
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
        ListaDeClientesToolStripMenuItem = New ToolStripMenuItem()
        ClientesToolStripMenuItem2 = New ToolStripMenuItem()
        FornecedoresToolStripMenuItem = New ToolStripMenuItem()
        InserirFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        ListaDeFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        MenuToolStripMenuItem = New ToolStripMenuItem()
        IrParaOMenuToolStripMenuItem = New ToolStripMenuItem()
        PedidosPendentesToolStripMenuItem = New ToolStripMenuItem()
        ArovarOuRejeitarToolStripMenuItem = New ToolStripMenuItem()
        Date1 = New DateTimePicker()
        lblDataFim = New Label()
        Date2 = New DateTimePicker()
        chkMultiplosDias = New CheckBox()
        txtObservacao = New TextBox()
        Label6 = New Label()
        Label1 = New Label()
        btnGravar = New Button()
        Label7 = New Label()
        Label5 = New Label()
        Label4 = New Label()
        Label3 = New Label()
        Label2 = New Label()
        txtEmail = New TextBox()
        txtTelefone = New TextBox()
        txtEmpresa = New TextBox()
        txtNome = New TextBox()
        chkAlmoco = New CheckBox()
        ComboBoxResponsavel = New ComboBox()
        MenuStrip1.SuspendLayout()
        SuspendLayout()
        ' 
        ' MenuStrip1
        ' 
        MenuStrip1.Items.AddRange(New ToolStripItem() {FicheiroToolStripMenuItem, DashboardToolStripMenuItem, VisitantesToolStripMenuItem, DadosToolStripMenuItem, ClientesToolStripMenuItem1, FornecedoresToolStripMenuItem, MenuToolStripMenuItem, PedidosPendentesToolStripMenuItem})
        MenuStrip1.Location = New Point(0, 0)
        MenuStrip1.Name = "MenuStrip1"
        MenuStrip1.Padding = New Padding(8, 3, 0, 3)
        MenuStrip1.Size = New Size(1423, 25)
        MenuStrip1.TabIndex = 35
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
        ClientesToolStripMenuItem1.DropDownItems.AddRange(New ToolStripItem() {ListaDeClientesToolStripMenuItem, ClientesToolStripMenuItem2})
        ClientesToolStripMenuItem1.Name = "ClientesToolStripMenuItem1"
        ClientesToolStripMenuItem1.Size = New Size(61, 19)
        ClientesToolStripMenuItem1.Text = "Clientes"
        ' 
        ' ListaDeClientesToolStripMenuItem
        ' 
        ListaDeClientesToolStripMenuItem.Name = "ListaDeClientesToolStripMenuItem"
        ListaDeClientesToolStripMenuItem.Size = New Size(159, 22)
        ListaDeClientesToolStripMenuItem.Text = "Inserir Clientes"
        ' 
        ' ClientesToolStripMenuItem2
        ' 
        ClientesToolStripMenuItem2.Name = "ClientesToolStripMenuItem2"
        ClientesToolStripMenuItem2.Size = New Size(159, 22)
        ClientesToolStripMenuItem2.Text = "Lista de Clientes"
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
        ' Date1
        ' 
        Date1.CalendarFont = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        Date1.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        Date1.Location = New Point(813, 170)
        Date1.Name = "Date1"
        Date1.Size = New Size(200, 29)
        Date1.TabIndex = 42
        ' 
        ' lblDataFim
        ' 
        lblDataFim.AutoSize = True
        lblDataFim.BackColor = Color.Transparent
        lblDataFim.Enabled = False
        lblDataFim.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        lblDataFim.ForeColor = Color.DeepSkyBlue
        lblDataFim.Location = New Point(1025, 125)
        lblDataFim.Name = "lblDataFim"
        lblDataFim.Size = New Size(76, 23)
        lblDataFim.TabIndex = 55
        lblDataFim.Text = "Data Fim:"
        ' 
        ' Date2
        ' 
        Date2.CalendarFont = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        Date2.Enabled = False
        Date2.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        Date2.Location = New Point(1025, 170)
        Date2.Name = "Date2"
        Date2.Size = New Size(200, 29)
        Date2.TabIndex = 56
        ' 
        ' chkMultiplosDias
        ' 
        chkMultiplosDias.AutoSize = True
        chkMultiplosDias.BackColor = SystemColors.GradientActiveCaption
        chkMultiplosDias.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        chkMultiplosDias.Location = New Point(1240, 170)
        chkMultiplosDias.Name = "chkMultiplosDias"
        chkMultiplosDias.Size = New Size(144, 27)
        chkMultiplosDias.TabIndex = 57
        chkMultiplosDias.Text = "Mais de um dia?"
        chkMultiplosDias.UseVisualStyleBackColor = False
        ' 
        ' txtObservacao
        ' 
        txtObservacao.BackColor = SystemColors.ScrollBar
        txtObservacao.Location = New Point(813, 373)
        txtObservacao.Margin = New Padding(4, 5, 4, 5)
        txtObservacao.Multiline = True
        txtObservacao.Name = "txtObservacao"
        txtObservacao.Size = New Size(382, 106)
        txtObservacao.TabIndex = 44
        ' 
        ' Label6
        ' 
        Label6.AutoSize = True
        Label6.BackColor = Color.Transparent
        Label6.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        Label6.ForeColor = Color.DeepSkyBlue
        Label6.Location = New Point(813, 328)
        Label6.Margin = New Padding(4, 0, 4, 0)
        Label6.Name = "Label6"
        Label6.Size = New Size(95, 23)
        Label6.TabIndex = 52
        Label6.Text = "Observação"
        ' 
        ' Label1
        ' 
        Label1.AutoSize = True
        Label1.BackColor = Color.Transparent
        Label1.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        Label1.ForeColor = Color.DeepSkyBlue
        Label1.Location = New Point(813, 231)
        Label1.Margin = New Padding(4, 0, 4, 0)
        Label1.Name = "Label1"
        Label1.Size = New Size(101, 23)
        Label1.TabIndex = 51
        Label1.Text = "Responsável"
        ' 
        ' btnGravar
        ' 
        btnGravar.BackColor = Color.DeepSkyBlue
        btnGravar.ForeColor = SystemColors.ControlLightLight
        btnGravar.Location = New Point(1107, 562)
        btnGravar.Margin = New Padding(4, 5, 4, 5)
        btnGravar.Name = "btnGravar"
        btnGravar.Size = New Size(88, 38)
        btnGravar.TabIndex = 45
        btnGravar.Text = "Gravar"
        btnGravar.UseVisualStyleBackColor = False
        ' 
        ' Label7
        ' 
        Label7.AutoSize = True
        Label7.BackColor = Color.Transparent
        Label7.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        Label7.ForeColor = Color.DeepSkyBlue
        Label7.Location = New Point(813, 125)
        Label7.Margin = New Padding(4, 0, 4, 0)
        Label7.Name = "Label7"
        Label7.Size = New Size(85, 23)
        Label7.TabIndex = 50
        Label7.Text = "Data Início:"
        ' 
        ' Label5
        ' 
        Label5.AutoSize = True
        Label5.BackColor = Color.Transparent
        Label5.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        Label5.ForeColor = Color.DeepSkyBlue
        Label5.Location = New Point(253, 435)
        Label5.Margin = New Padding(4, 0, 4, 0)
        Label5.Name = "Label5"
        Label5.Size = New Size(48, 23)
        Label5.TabIndex = 49
        Label5.Text = "Email"
        ' 
        ' Label4
        ' 
        Label4.AutoSize = True
        Label4.BackColor = Color.Transparent
        Label4.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        Label4.ForeColor = Color.DeepSkyBlue
        Label4.Location = New Point(253, 328)
        Label4.Margin = New Padding(4, 0, 4, 0)
        Label4.Name = "Label4"
        Label4.Size = New Size(70, 23)
        Label4.TabIndex = 48
        Label4.Text = "Telefone"
        ' 
        ' Label3
        ' 
        Label3.AutoSize = True
        Label3.BackColor = Color.Transparent
        Label3.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        Label3.ForeColor = Color.DeepSkyBlue
        Label3.Location = New Point(253, 231)
        Label3.Margin = New Padding(4, 0, 4, 0)
        Label3.Name = "Label3"
        Label3.Size = New Size(73, 23)
        Label3.TabIndex = 47
        Label3.Text = "Empresa"
        ' 
        ' Label2
        ' 
        Label2.AutoSize = True
        Label2.BackColor = Color.Transparent
        Label2.Font = New Font("Arial Narrow", 14.25F, FontStyle.Bold, GraphicsUnit.Point, CByte(0))
        Label2.ForeColor = Color.DeepSkyBlue
        Label2.Location = New Point(253, 125)
        Label2.Margin = New Padding(4, 0, 4, 0)
        Label2.Name = "Label2"
        Label2.Size = New Size(54, 23)
        Label2.TabIndex = 46
        Label2.Text = "Nome"
        ' 
        ' txtEmail
        ' 
        txtEmail.BackColor = SystemColors.ScrollBar
        txtEmail.Location = New Point(253, 478)
        txtEmail.Margin = New Padding(4, 5, 4, 5)
        txtEmail.Name = "txtEmail"
        txtEmail.Size = New Size(382, 23)
        txtEmail.TabIndex = 41
        ' 
        ' txtTelefone
        ' 
        txtTelefone.BackColor = SystemColors.ScrollBar
        txtTelefone.Location = New Point(253, 373)
        txtTelefone.Margin = New Padding(4, 5, 4, 5)
        txtTelefone.Name = "txtTelefone"
        txtTelefone.Size = New Size(382, 23)
        txtTelefone.TabIndex = 40
        ' 
        ' txtEmpresa
        ' 
        txtEmpresa.BackColor = SystemColors.ScrollBar
        txtEmpresa.Location = New Point(253, 273)
        txtEmpresa.Margin = New Padding(4, 5, 4, 5)
        txtEmpresa.Name = "txtEmpresa"
        txtEmpresa.Size = New Size(382, 23)
        txtEmpresa.TabIndex = 39
        ' 
        ' txtNome
        ' 
        txtNome.BackColor = SystemColors.ScrollBar
        txtNome.Location = New Point(253, 172)
        txtNome.Margin = New Padding(4, 5, 4, 5)
        txtNome.Name = "txtNome"
        txtNome.Size = New Size(382, 23)
        txtNome.TabIndex = 38
        ' 
        ' chkAlmoco
        ' 
        chkAlmoco.AutoSize = True
        chkAlmoco.BackColor = SystemColors.GradientActiveCaption
        chkAlmoco.Font = New Font("Arial Narrow", 14.25F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        chkAlmoco.Location = New Point(813, 497)
        chkAlmoco.Name = "chkAlmoco"
        chkAlmoco.Size = New Size(81, 27)
        chkAlmoco.TabIndex = 53
        chkAlmoco.Text = "Almoço"
        chkAlmoco.UseVisualStyleBackColor = False
        ' 
        ' ComboBoxResponsavel
        ' 
        ComboBoxResponsavel.DropDownStyle = ComboBoxStyle.DropDownList
        ComboBoxResponsavel.Font = New Font("Segoe UI", 14F)
        ComboBoxResponsavel.FormattingEnabled = True
        ComboBoxResponsavel.Items.AddRange(New Object() {"Commercial Team", "Compras", "IT", "Logistica", "Manutencao", "Producao", "Qualidade", "Carlos Balata", "Emilio Vigia", "Fernando Xavier", "Filipe Loureiro", "Joao Monteiro", "Micael Dias", "Pedro Bonifacio", "Rui Novo", "Veronica Rosa", "Virginia Lopes", "Monica Vicente", "Pedro Vicente", "Telmo Febra", "Henrique Carvalho", "Joao Bernardino", "Centro Ensaios"})
        ComboBoxResponsavel.Location = New Point(813, 273)
        ComboBoxResponsavel.Name = "ComboBoxResponsavel"
        ComboBoxResponsavel.Size = New Size(382, 33)
        ComboBoxResponsavel.TabIndex = 54
        ' 
        ' InserirVisitantesFornecedores
        ' 
        AutoScaleDimensions = New SizeF(7F, 15F)
        AutoScaleMode = AutoScaleMode.Font
        BackgroundImage = CType(resources.GetObject("$this.BackgroundImage"), Image)
        BackgroundImageLayout = ImageLayout.Stretch
        ClientSize = New Size(1423, 651)
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
        Name = "InserirVisitantesFornecedores"
        StartPosition = FormStartPosition.CenterScreen
        Text = "Visitantes Fornecedores"
        MenuStrip1.ResumeLayout(False)
        MenuStrip1.PerformLayout()
        ResumeLayout(False)
        PerformLayout()
    End Sub

    Friend WithEvents MenuStrip1 As MenuStrip
    Friend WithEvents FicheiroToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents SairToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents DashboardToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficoEmpresasToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficoTotalVisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents VisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaComFotoToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents DadosToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ClientesToolStripMenuItem1 As ToolStripMenuItem
    Friend WithEvents ListaDeClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents PedidosPendentesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ArovarOuRejeitarToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents MenuToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents IrParaOMenuToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents Date1 As DateTimePicker
    Friend WithEvents txtObservacao As TextBox
    Friend WithEvents Label6 As Label
    Friend WithEvents Label1 As Label
    Friend WithEvents btnGravar As Button
    Friend WithEvents Label7 As Label
    Friend WithEvents Label5 As Label
    Friend WithEvents Label4 As Label
    Friend WithEvents Label3 As Label
    Friend WithEvents Label2 As Label
    Friend WithEvents txtEmail As TextBox
    Friend WithEvents txtTelefone As TextBox
    Friend WithEvents txtEmpresa As TextBox
    Friend WithEvents txtNome As TextBox
    Friend WithEvents FornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents InserirFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ClientesToolStripMenuItem2 As ToolStripMenuItem
    Friend WithEvents VisitasFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeVisitantesFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents chkAlmoco As CheckBox
    Friend WithEvents ComboBoxResponsavel As ComboBox
    Friend WithEvents lblDataFim As Label
    Friend WithEvents Date2 As DateTimePicker
    Friend WithEvents chkMultiplosDias As CheckBox
End Class
