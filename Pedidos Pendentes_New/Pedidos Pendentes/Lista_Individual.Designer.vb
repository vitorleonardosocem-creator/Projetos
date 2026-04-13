<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Lista_Individual
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
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(Lista_Individual))
        txtID = New TextBox()
        txtNome = New TextBox()
        txtEmpresa = New TextBox()
        txtTelefone = New TextBox()
        txtEmail = New TextBox()
        Label1 = New Label()
        Label2 = New Label()
        Label3 = New Label()
        Label4 = New Label()
        Label5 = New Label()
        Label7 = New Label()
        btnEsquerda = New Button()
        btnDireita = New Button()
        MenuStrip1 = New MenuStrip()
        FicheiroToolStripMenuItem = New ToolStripMenuItem()
        SairToolStripMenuItem = New ToolStripMenuItem()
        DashboardToolStripMenuItem = New ToolStripMenuItem()
        GraficoEmpresasToolStripMenuItem = New ToolStripMenuItem()
        GraficoTotalVisitantesToolStripMenuItem = New ToolStripMenuItem()
        VisitantesToolStripMenuItem = New ToolStripMenuItem()
        ListaToolStripMenuItem = New ToolStripMenuItem()
        ListaDeVisitantesIndividualToolStripMenuItem = New ToolStripMenuItem()
        ListaDeVisitantesFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        DadosToolStripMenuItem = New ToolStripMenuItem()
        ClientesToolStripMenuItem = New ToolStripMenuItem()
        ClientesToolStripMenuItem1 = New ToolStripMenuItem()
        ClientesToolStripMenuItem2 = New ToolStripMenuItem()
        ListaDeClientesToolStripMenuItem = New ToolStripMenuItem()
        ListaDeClientesToolStripMenuItem1 = New ToolStripMenuItem()
        FornecedoresToolStripMenuItem = New ToolStripMenuItem()
        InserirFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        ListaDeFornecedoresToolStripMenuItem = New ToolStripMenuItem()
        PedidosPendentesToolStripMenuItem = New ToolStripMenuItem()
        ArovarOuRejeitarToolStripMenuItem = New ToolStripMenuItem()
        MenuToolStripMenuItem = New ToolStripMenuItem()
        IrParaOMenuToolStripMenuItem = New ToolStripMenuItem()
        Button1 = New Button()
        PictureBox1 = New PictureBox()
        btnEditar = New Button()
        Date2 = New DateTimePicker()
        Label9 = New Label()
        Label8 = New Label()
        txtResponsavel = New TextBox()
        txtObservacao = New TextBox()
        Label6 = New Label()
        txtConfirmado = New TextBox()
        btnDuplicar = New Button()
        Label10 = New Label()
        txtAlmoco = New TextBox()
        MenuStrip1.SuspendLayout()
        CType(PictureBox1, ComponentModel.ISupportInitialize).BeginInit()
        SuspendLayout()
        ' 
        ' txtID
        ' 
        txtID.BackColor = SystemColors.ScrollBar
        txtID.Location = New Point(72, 120)
        txtID.Name = "txtID"
        txtID.Size = New Size(298, 23)
        txtID.TabIndex = 1
        ' 
        ' txtNome
        ' 
        txtNome.BackColor = SystemColors.ScrollBar
        txtNome.Location = New Point(72, 182)
        txtNome.Name = "txtNome"
        txtNome.Size = New Size(298, 23)
        txtNome.TabIndex = 2
        ' 
        ' txtEmpresa
        ' 
        txtEmpresa.BackColor = SystemColors.ScrollBar
        txtEmpresa.Location = New Point(72, 245)
        txtEmpresa.Name = "txtEmpresa"
        txtEmpresa.Size = New Size(298, 23)
        txtEmpresa.TabIndex = 3
        ' 
        ' txtTelefone
        ' 
        txtTelefone.BackColor = SystemColors.ScrollBar
        txtTelefone.Location = New Point(72, 312)
        txtTelefone.Name = "txtTelefone"
        txtTelefone.Size = New Size(298, 23)
        txtTelefone.TabIndex = 4
        ' 
        ' txtEmail
        ' 
        txtEmail.BackColor = SystemColors.ScrollBar
        txtEmail.Location = New Point(72, 375)
        txtEmail.Name = "txtEmail"
        txtEmail.Size = New Size(298, 23)
        txtEmail.TabIndex = 5
        ' 
        ' Label1
        ' 
        Label1.AutoSize = True
        Label1.BackColor = Color.Transparent
        Label1.Font = New Font("Segoe UI", 12F)
        Label1.ForeColor = Color.DeepSkyBlue
        Label1.Location = New Point(72, 96)
        Label1.Name = "Label1"
        Label1.Size = New Size(25, 21)
        Label1.TabIndex = 8
        Label1.Text = "ID"
        ' 
        ' Label2
        ' 
        Label2.AutoSize = True
        Label2.BackColor = Color.Transparent
        Label2.Font = New Font("Segoe UI", 12F)
        Label2.ForeColor = Color.DeepSkyBlue
        Label2.Location = New Point(72, 159)
        Label2.Name = "Label2"
        Label2.Size = New Size(53, 21)
        Label2.TabIndex = 9
        Label2.Text = "Nome"
        ' 
        ' Label3
        ' 
        Label3.AutoSize = True
        Label3.BackColor = Color.Transparent
        Label3.Font = New Font("Segoe UI", 12F)
        Label3.ForeColor = Color.DeepSkyBlue
        Label3.Location = New Point(72, 222)
        Label3.Name = "Label3"
        Label3.Size = New Size(70, 21)
        Label3.TabIndex = 10
        Label3.Text = "Empresa"
        ' 
        ' Label4
        ' 
        Label4.AutoSize = True
        Label4.BackColor = Color.Transparent
        Label4.Font = New Font("Segoe UI", 12F)
        Label4.ForeColor = Color.DeepSkyBlue
        Label4.Location = New Point(72, 287)
        Label4.Name = "Label4"
        Label4.Size = New Size(67, 21)
        Label4.TabIndex = 11
        Label4.Text = "Telefone"
        ' 
        ' Label5
        ' 
        Label5.AutoSize = True
        Label5.BackColor = Color.Transparent
        Label5.Font = New Font("Segoe UI", 12F)
        Label5.ForeColor = Color.DeepSkyBlue
        Label5.Location = New Point(72, 351)
        Label5.Name = "Label5"
        Label5.Size = New Size(48, 21)
        Label5.TabIndex = 12
        Label5.Text = "Email"
        ' 
        ' Label7
        ' 
        Label7.AutoSize = True
        Label7.BackColor = Color.Transparent
        Label7.Font = New Font("Segoe UI", 12F)
        Label7.ForeColor = Color.DeepSkyBlue
        Label7.Location = New Point(72, 416)
        Label7.Name = "Label7"
        Label7.Size = New Size(42, 21)
        Label7.TabIndex = 14
        Label7.Text = "Data"
        ' 
        ' btnEsquerda
        ' 
        btnEsquerda.BackColor = Color.DeepSkyBlue
        btnEsquerda.Location = New Point(72, 778)
        btnEsquerda.Name = "btnEsquerda"
        btnEsquerda.Size = New Size(41, 23)
        btnEsquerda.TabIndex = 15
        btnEsquerda.Text = "<"
        btnEsquerda.UseVisualStyleBackColor = False
        ' 
        ' btnDireita
        ' 
        btnDireita.BackColor = Color.DeepSkyBlue
        btnDireita.Location = New Point(144, 778)
        btnDireita.Name = "btnDireita"
        btnDireita.Size = New Size(41, 23)
        btnDireita.TabIndex = 16
        btnDireita.Text = ">"
        btnDireita.UseVisualStyleBackColor = False
        ' 
        ' MenuStrip1
        ' 
        MenuStrip1.Items.AddRange(New ToolStripItem() {FicheiroToolStripMenuItem, DashboardToolStripMenuItem, VisitantesToolStripMenuItem, DadosToolStripMenuItem, ClientesToolStripMenuItem2, FornecedoresToolStripMenuItem, PedidosPendentesToolStripMenuItem, MenuToolStripMenuItem})
        MenuStrip1.Location = New Point(0, 0)
        MenuStrip1.Name = "MenuStrip1"
        MenuStrip1.Size = New Size(1730, 24)
        MenuStrip1.TabIndex = 17
        MenuStrip1.Text = "MenuStrip1"
        ' 
        ' FicheiroToolStripMenuItem
        ' 
        FicheiroToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {SairToolStripMenuItem})
        FicheiroToolStripMenuItem.Name = "FicheiroToolStripMenuItem"
        FicheiroToolStripMenuItem.Size = New Size(61, 20)
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
        DashboardToolStripMenuItem.Size = New Size(76, 20)
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
        VisitantesToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {ListaToolStripMenuItem, ListaDeVisitantesIndividualToolStripMenuItem, ListaDeVisitantesFornecedoresToolStripMenuItem})
        VisitantesToolStripMenuItem.Name = "VisitantesToolStripMenuItem"
        VisitantesToolStripMenuItem.Size = New Size(112, 20)
        VisitantesToolStripMenuItem.Text = "Lista de Visitantes"
        ' 
        ' ListaToolStripMenuItem
        ' 
        ListaToolStripMenuItem.Name = "ListaToolStripMenuItem"
        ListaToolStripMenuItem.Size = New Size(240, 22)
        ListaToolStripMenuItem.Text = "Lista de visitantes Clientes"
        ' 
        ' ListaDeVisitantesIndividualToolStripMenuItem
        ' 
        ListaDeVisitantesIndividualToolStripMenuItem.Name = "ListaDeVisitantesIndividualToolStripMenuItem"
        ListaDeVisitantesIndividualToolStripMenuItem.Size = New Size(240, 22)
        ListaDeVisitantesIndividualToolStripMenuItem.Text = "Lista de visitantes Individual"
        ' 
        ' ListaDeVisitantesFornecedoresToolStripMenuItem
        ' 
        ListaDeVisitantesFornecedoresToolStripMenuItem.Name = "ListaDeVisitantesFornecedoresToolStripMenuItem"
        ListaDeVisitantesFornecedoresToolStripMenuItem.Size = New Size(240, 22)
        ListaDeVisitantesFornecedoresToolStripMenuItem.Text = "Lista de visitantes Fornecedores"
        ' 
        ' DadosToolStripMenuItem
        ' 
        DadosToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {ClientesToolStripMenuItem, ClientesToolStripMenuItem1})
        DadosToolStripMenuItem.Name = "DadosToolStripMenuItem"
        DadosToolStripMenuItem.Size = New Size(52, 20)
        DadosToolStripMenuItem.Text = "Visitas"
        ' 
        ' ClientesToolStripMenuItem
        ' 
        ClientesToolStripMenuItem.Name = "ClientesToolStripMenuItem"
        ClientesToolStripMenuItem.Size = New Size(181, 22)
        ClientesToolStripMenuItem.Text = "Visitas Clientes"
        ' 
        ' ClientesToolStripMenuItem1
        ' 
        ClientesToolStripMenuItem1.Name = "ClientesToolStripMenuItem1"
        ClientesToolStripMenuItem1.Size = New Size(181, 22)
        ClientesToolStripMenuItem1.Text = "Visitas Fornecedores"
        ' 
        ' ClientesToolStripMenuItem2
        ' 
        ClientesToolStripMenuItem2.DropDownItems.AddRange(New ToolStripItem() {ListaDeClientesToolStripMenuItem, ListaDeClientesToolStripMenuItem1})
        ClientesToolStripMenuItem2.Name = "ClientesToolStripMenuItem2"
        ClientesToolStripMenuItem2.Size = New Size(61, 20)
        ClientesToolStripMenuItem2.Text = "Clientes"
        ' 
        ' ListaDeClientesToolStripMenuItem
        ' 
        ListaDeClientesToolStripMenuItem.Name = "ListaDeClientesToolStripMenuItem"
        ListaDeClientesToolStripMenuItem.Size = New Size(159, 22)
        ListaDeClientesToolStripMenuItem.Text = "Inserir Clientes"
        ' 
        ' ListaDeClientesToolStripMenuItem1
        ' 
        ListaDeClientesToolStripMenuItem1.Name = "ListaDeClientesToolStripMenuItem1"
        ListaDeClientesToolStripMenuItem1.Size = New Size(159, 22)
        ListaDeClientesToolStripMenuItem1.Text = "Lista de Clientes"
        ' 
        ' FornecedoresToolStripMenuItem
        ' 
        FornecedoresToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {InserirFornecedoresToolStripMenuItem, ListaDeFornecedoresToolStripMenuItem})
        FornecedoresToolStripMenuItem.Name = "FornecedoresToolStripMenuItem"
        FornecedoresToolStripMenuItem.Size = New Size(90, 20)
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
        PedidosPendentesToolStripMenuItem.Size = New Size(119, 20)
        PedidosPendentesToolStripMenuItem.Text = "Pedidos Pendentes"
        ' 
        ' ArovarOuRejeitarToolStripMenuItem
        ' 
        ArovarOuRejeitarToolStripMenuItem.Name = "ArovarOuRejeitarToolStripMenuItem"
        ArovarOuRejeitarToolStripMenuItem.Size = New Size(168, 22)
        ArovarOuRejeitarToolStripMenuItem.Text = "Arovar ou Rejeitar"
        ' 
        ' MenuToolStripMenuItem
        ' 
        MenuToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {IrParaOMenuToolStripMenuItem})
        MenuToolStripMenuItem.Name = "MenuToolStripMenuItem"
        MenuToolStripMenuItem.Size = New Size(50, 20)
        MenuToolStripMenuItem.Text = "Menu"
        ' 
        ' IrParaOMenuToolStripMenuItem
        ' 
        IrParaOMenuToolStripMenuItem.Name = "IrParaOMenuToolStripMenuItem"
        IrParaOMenuToolStripMenuItem.Size = New Size(151, 22)
        IrParaOMenuToolStripMenuItem.Text = "Ir para o Menu"
        ' 
        ' Button1
        ' 
        Button1.BackColor = SystemColors.AppWorkspace
        Button1.BackgroundImage = CType(resources.GetObject("Button1.BackgroundImage"), Image)
        Button1.BackgroundImageLayout = ImageLayout.Zoom
        Button1.Location = New Point(326, 769)
        Button1.Name = "Button1"
        Button1.Size = New Size(43, 40)
        Button1.TabIndex = 18
        Button1.UseVisualStyleBackColor = False
        ' 
        ' PictureBox1
        ' 
        PictureBox1.Image = CType(resources.GetObject("PictureBox1.Image"), Image)
        PictureBox1.Location = New Point(457, 65)
        PictureBox1.Name = "PictureBox1"
        PictureBox1.Size = New Size(1261, 768)
        PictureBox1.TabIndex = 19
        PictureBox1.TabStop = False
        ' 
        ' btnEditar
        ' 
        btnEditar.BackgroundImage = CType(resources.GetObject("btnEditar.BackgroundImage"), Image)
        btnEditar.BackgroundImageLayout = ImageLayout.Zoom
        btnEditar.Location = New Point(228, 770)
        btnEditar.Name = "btnEditar"
        btnEditar.Size = New Size(43, 39)
        btnEditar.TabIndex = 20
        btnEditar.UseVisualStyleBackColor = True
        ' 
        ' Date2
        ' 
        Date2.Location = New Point(72, 440)
        Date2.Name = "Date2"
        Date2.Size = New Size(298, 23)
        Date2.TabIndex = 21
        ' 
        ' Label9
        ' 
        Label9.AutoSize = True
        Label9.BackColor = Color.Transparent
        Label9.Font = New Font("Segoe UI", 12F)
        Label9.ForeColor = Color.DeepSkyBlue
        Label9.Location = New Point(72, 544)
        Label9.Name = "Label9"
        Label9.Size = New Size(92, 21)
        Label9.TabIndex = 22
        Label9.Text = "Observação"
        ' 
        ' Label8
        ' 
        Label8.AutoSize = True
        Label8.BackColor = Color.Transparent
        Label8.Font = New Font("Segoe UI", 12F)
        Label8.ForeColor = Color.DeepSkyBlue
        Label8.Location = New Point(72, 480)
        Label8.Name = "Label8"
        Label8.Size = New Size(97, 21)
        Label8.TabIndex = 23
        Label8.Text = "Responsável"
        ' 
        ' txtResponsavel
        ' 
        txtResponsavel.BackColor = SystemColors.ScrollBar
        txtResponsavel.Location = New Point(72, 504)
        txtResponsavel.Name = "txtResponsavel"
        txtResponsavel.Size = New Size(298, 23)
        txtResponsavel.TabIndex = 24
        ' 
        ' txtObservacao
        ' 
        txtObservacao.BackColor = SystemColors.ScrollBar
        txtObservacao.Location = New Point(72, 568)
        txtObservacao.Name = "txtObservacao"
        txtObservacao.Size = New Size(298, 23)
        txtObservacao.TabIndex = 25
        ' 
        ' Label6
        ' 
        Label6.AutoSize = True
        Label6.BackColor = Color.Transparent
        Label6.Font = New Font("Segoe UI", 12F)
        Label6.ForeColor = Color.DeepSkyBlue
        Label6.Location = New Point(72, 612)
        Label6.Name = "Label6"
        Label6.Size = New Size(93, 21)
        Label6.TabIndex = 26
        Label6.Text = "Confirmado"
        ' 
        ' txtConfirmado
        ' 
        txtConfirmado.BackColor = SystemColors.ScrollBar
        txtConfirmado.Location = New Point(72, 636)
        txtConfirmado.Name = "txtConfirmado"
        txtConfirmado.Size = New Size(298, 23)
        txtConfirmado.TabIndex = 27
        ' 
        ' btnDuplicar
        ' 
        btnDuplicar.BackgroundImage = CType(resources.GetObject("btnDuplicar.BackgroundImage"), Image)
        btnDuplicar.BackgroundImageLayout = ImageLayout.Zoom
        btnDuplicar.Location = New Point(277, 770)
        btnDuplicar.Name = "btnDuplicar"
        btnDuplicar.Size = New Size(43, 39)
        btnDuplicar.TabIndex = 28
        btnDuplicar.UseVisualStyleBackColor = True
        ' 
        ' Label10
        ' 
        Label10.AutoSize = True
        Label10.BackColor = Color.Transparent
        Label10.Font = New Font("Segoe UI", 12F)
        Label10.ForeColor = Color.DeepSkyBlue
        Label10.Location = New Point(71, 676)
        Label10.Name = "Label10"
        Label10.Size = New Size(63, 21)
        Label10.TabIndex = 29
        Label10.Text = "Almoço"
        ' 
        ' txtAlmoco
        ' 
        txtAlmoco.BackColor = SystemColors.ScrollBar
        txtAlmoco.Location = New Point(71, 709)
        txtAlmoco.Name = "txtAlmoco"
        txtAlmoco.Size = New Size(298, 23)
        txtAlmoco.TabIndex = 30
        ' 
        ' Lista_Individual
        ' 
        AutoScaleDimensions = New SizeF(7F, 15F)
        AutoScaleMode = AutoScaleMode.Font
        ClientSize = New Size(1730, 864)
        Controls.Add(txtAlmoco)
        Controls.Add(Label10)
        Controls.Add(btnDuplicar)
        Controls.Add(txtConfirmado)
        Controls.Add(Label6)
        Controls.Add(txtObservacao)
        Controls.Add(txtResponsavel)
        Controls.Add(Label8)
        Controls.Add(Label9)
        Controls.Add(Date2)
        Controls.Add(btnEditar)
        Controls.Add(PictureBox1)
        Controls.Add(Button1)
        Controls.Add(btnDireita)
        Controls.Add(btnEsquerda)
        Controls.Add(Label7)
        Controls.Add(Label5)
        Controls.Add(Label4)
        Controls.Add(Label3)
        Controls.Add(Label2)
        Controls.Add(Label1)
        Controls.Add(txtEmail)
        Controls.Add(txtTelefone)
        Controls.Add(txtEmpresa)
        Controls.Add(txtNome)
        Controls.Add(txtID)
        Controls.Add(MenuStrip1)
        MainMenuStrip = MenuStrip1
        Name = "Lista_Individual"
        StartPosition = FormStartPosition.CenterScreen
        Text = "Lista Individual"
        WindowState = FormWindowState.Maximized
        MenuStrip1.ResumeLayout(False)
        MenuStrip1.PerformLayout()
        CType(PictureBox1, ComponentModel.ISupportInitialize).EndInit()
        ResumeLayout(False)
        PerformLayout()
    End Sub
    Friend WithEvents txtID As TextBox
    Friend WithEvents txtNome As TextBox
    Friend WithEvents txtEmpresa As TextBox
    Friend WithEvents txtTelefone As TextBox
    Friend WithEvents txtEmail As TextBox
    Friend WithEvents Label1 As Label
    Friend WithEvents Label2 As Label
    Friend WithEvents Label3 As Label
    Friend WithEvents Label4 As Label
    Friend WithEvents Label5 As Label
    Friend WithEvents Label7 As Label
    Friend WithEvents btnEsquerda As Button
    Friend WithEvents btnDireita As Button
    Friend WithEvents MenuStrip1 As MenuStrip
    Friend WithEvents FicheiroToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents SairToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents DashboardToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficoEmpresasToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficoTotalVisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents VisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents PedidosPendentesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ArovarOuRejeitarToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents MenuToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents IrParaOMenuToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents DadosToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents Button1 As Button
    Friend WithEvents PictureBox1 As PictureBox
    Friend WithEvents btnEditar As Button
    Friend WithEvents Date2 As DateTimePicker
    Friend WithEvents Label9 As Label
    Friend WithEvents Label8 As Label
    Friend WithEvents txtResponsavel As TextBox
    Friend WithEvents txtObservacao As TextBox
    Friend WithEvents Label6 As Label
    Friend WithEvents txtConfirmado As TextBox
    Friend WithEvents btnDuplicar As Button
    Friend WithEvents Label10 As Label
    Friend WithEvents txtAlmoco As TextBox
    Friend WithEvents ClientesToolStripMenuItem1 As ToolStripMenuItem
    Friend WithEvents ClientesToolStripMenuItem2 As ToolStripMenuItem
    Friend WithEvents ListaDeClientesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents FornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents InserirFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeFornecedoresToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeClientesToolStripMenuItem1 As ToolStripMenuItem
    Friend WithEvents ListaDeVisitantesIndividualToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaDeVisitantesFornecedoresToolStripMenuItem As ToolStripMenuItem
End Class
