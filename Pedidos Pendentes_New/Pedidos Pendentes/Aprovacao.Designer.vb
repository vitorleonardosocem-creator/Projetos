<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class Aprovacao
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()>
    Protected Overrides Sub Dispose(disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()>
    Private Sub InitializeComponent()
        dgvPedidosPendentes = New DataGridView()
        Id = New DataGridViewTextBoxColumn()
        Nome = New DataGridViewTextBoxColumn()
        Empresa = New DataGridViewTextBoxColumn()
        Telefone = New DataGridViewTextBoxColumn()
        Email = New DataGridViewTextBoxColumn()
        Data = New DataGridViewTextBoxColumn()
        btnAprovar = New Button()
        btnCancelar = New Button()
        lblStatus = New Label()
        MenuStrip1 = New MenuStrip()
        MenuToolStripMenuItem = New ToolStripMenuItem()
        SairToolStripMenuItem = New ToolStripMenuItem()
        DashboardToolStripMenuItem = New ToolStripMenuItem()
        GraficosToolStripMenuItem = New ToolStripMenuItem()
        GraficoTotalVisitantesToolStripMenuItem = New ToolStripMenuItem()
        VisitantesToolStripMenuItem = New ToolStripMenuItem()
        ListaToolStripMenuItem = New ToolStripMenuItem()
        ListaComFotoToolStripMenuItem = New ToolStripMenuItem()
        DadosToolStripMenuItem = New ToolStripMenuItem()
        ClientesToolStripMenuItem = New ToolStripMenuItem()
        MenuToolStripMenuItem1 = New ToolStripMenuItem()
        MenuToolStripMenuItem2 = New ToolStripMenuItem()
        CType(dgvPedidosPendentes, ComponentModel.ISupportInitialize).BeginInit()
        MenuStrip1.SuspendLayout()
        SuspendLayout()
        ' 
        ' dgvPedidosPendentes
        ' 
        dgvPedidosPendentes.AllowUserToAddRows = False
        dgvPedidosPendentes.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
        dgvPedidosPendentes.BackgroundColor = SystemColors.Control
        dgvPedidosPendentes.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.AutoSize
        dgvPedidosPendentes.Columns.AddRange(New DataGridViewColumn() {Id, Nome, Empresa, Telefone, Email, Data})
        dgvPedidosPendentes.Dock = DockStyle.Fill
        dgvPedidosPendentes.Location = New Point(0, 24)
        dgvPedidosPendentes.Margin = New Padding(3, 4, 3, 4)
        dgvPedidosPendentes.Name = "dgvPedidosPendentes"
        dgvPedidosPendentes.ReadOnly = True
        dgvPedidosPendentes.RowHeadersWidth = 62
        dgvPedidosPendentes.SelectionMode = DataGridViewSelectionMode.FullRowSelect
        dgvPedidosPendentes.Size = New Size(1793, 787)
        dgvPedidosPendentes.TabIndex = 0
        ' 
        ' Id
        ' 
        Id.HeaderText = "ID"
        Id.MinimumWidth = 8
        Id.Name = "Id"
        Id.ReadOnly = True
        ' 
        ' Nome
        ' 
        Nome.HeaderText = "Nome"
        Nome.MinimumWidth = 8
        Nome.Name = "Nome"
        Nome.ReadOnly = True
        ' 
        ' Empresa
        ' 
        Empresa.HeaderText = "Empresa"
        Empresa.MinimumWidth = 8
        Empresa.Name = "Empresa"
        Empresa.ReadOnly = True
        ' 
        ' Telefone
        ' 
        Telefone.HeaderText = "Telefone"
        Telefone.MinimumWidth = 8
        Telefone.Name = "Telefone"
        Telefone.ReadOnly = True
        ' 
        ' Email
        ' 
        Email.HeaderText = "Email"
        Email.MinimumWidth = 8
        Email.Name = "Email"
        Email.ReadOnly = True
        ' 
        ' Data
        ' 
        Data.HeaderText = "Data"
        Data.MinimumWidth = 8
        Data.Name = "Data"
        Data.ReadOnly = True
        ' 
        ' btnAprovar
        ' 
        btnAprovar.BackColor = Color.LimeGreen
        btnAprovar.Font = New Font("Arial Narrow", 12F, FontStyle.Bold, GraphicsUnit.Point, CByte(0))
        btnAprovar.ForeColor = Color.White
        btnAprovar.Location = New Point(1178, 596)
        btnAprovar.Margin = New Padding(3, 4, 3, 4)
        btnAprovar.Name = "btnAprovar"
        btnAprovar.Size = New Size(130, 35)
        btnAprovar.TabIndex = 1
        btnAprovar.Text = "Aprovar"
        btnAprovar.UseVisualStyleBackColor = False
        ' 
        ' btnCancelar
        ' 
        btnCancelar.BackColor = Color.Red
        btnCancelar.Font = New Font("Arial Narrow", 12F, FontStyle.Bold, GraphicsUnit.Point, CByte(0))
        btnCancelar.ForeColor = Color.White
        btnCancelar.Location = New Point(1330, 597)
        btnCancelar.Margin = New Padding(3, 4, 3, 4)
        btnCancelar.Name = "btnCancelar"
        btnCancelar.Size = New Size(130, 34)
        btnCancelar.TabIndex = 2
        btnCancelar.Text = "Recusar"
        btnCancelar.UseVisualStyleBackColor = False
        ' 
        ' lblStatus
        ' 
        lblStatus.AutoSize = True
        lblStatus.BackColor = Color.Transparent
        lblStatus.Font = New Font("Arial Narrow", 14F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        lblStatus.ForeColor = Color.DeepSkyBlue
        lblStatus.Location = New Point(1226, 547)
        lblStatus.Name = "lblStatus"
        lblStatus.Size = New Size(175, 23)
        lblStatus.TabIndex = 3
        lblStatus.Text = "Aguardando aprovação"
        ' 
        ' MenuStrip1
        ' 
        MenuStrip1.ImageScalingSize = New Size(24, 24)
        MenuStrip1.Items.AddRange(New ToolStripItem() {MenuToolStripMenuItem, DashboardToolStripMenuItem, VisitantesToolStripMenuItem, DadosToolStripMenuItem, MenuToolStripMenuItem1})
        MenuStrip1.Location = New Point(0, 0)
        MenuStrip1.Name = "MenuStrip1"
        MenuStrip1.Size = New Size(1793, 24)
        MenuStrip1.TabIndex = 4
        MenuStrip1.Text = "MenuStrip1"
        ' 
        ' MenuToolStripMenuItem
        ' 
        MenuToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {SairToolStripMenuItem})
        MenuToolStripMenuItem.Name = "MenuToolStripMenuItem"
        MenuToolStripMenuItem.Size = New Size(61, 20)
        MenuToolStripMenuItem.Text = "Ficheiro"
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
        DashboardToolStripMenuItem.Size = New Size(76, 20)
        DashboardToolStripMenuItem.Text = "Dashboard"
        ' 
        ' GraficosToolStripMenuItem
        ' 
        GraficosToolStripMenuItem.Name = "GraficosToolStripMenuItem"
        GraficosToolStripMenuItem.Size = New Size(193, 22)
        GraficosToolStripMenuItem.Text = "Grafico Empresas"
        ' 
        ' GraficoTotalVisitantesToolStripMenuItem
        ' 
        GraficoTotalVisitantesToolStripMenuItem.Name = "GraficoTotalVisitantesToolStripMenuItem"
        GraficoTotalVisitantesToolStripMenuItem.Size = New Size(193, 22)
        GraficoTotalVisitantesToolStripMenuItem.Text = "Grafico Total Visitantes"
        ' 
        ' VisitantesToolStripMenuItem
        ' 
        VisitantesToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {ListaToolStripMenuItem, ListaComFotoToolStripMenuItem})
        VisitantesToolStripMenuItem.Name = "VisitantesToolStripMenuItem"
        VisitantesToolStripMenuItem.Size = New Size(69, 20)
        VisitantesToolStripMenuItem.Text = "Visitantes"
        ' 
        ' ListaToolStripMenuItem
        ' 
        ListaToolStripMenuItem.Name = "ListaToolStripMenuItem"
        ListaToolStripMenuItem.Size = New Size(150, 22)
        ListaToolStripMenuItem.Text = "Lista"
        ' 
        ' ListaComFotoToolStripMenuItem
        ' 
        ListaComFotoToolStripMenuItem.Name = "ListaComFotoToolStripMenuItem"
        ListaComFotoToolStripMenuItem.Size = New Size(150, 22)
        ListaComFotoToolStripMenuItem.Text = "Lista com foto"
        ' 
        ' DadosToolStripMenuItem
        ' 
        DadosToolStripMenuItem.DropDownItems.AddRange(New ToolStripItem() {ClientesToolStripMenuItem})
        DadosToolStripMenuItem.Name = "DadosToolStripMenuItem"
        DadosToolStripMenuItem.Size = New Size(52, 20)
        DadosToolStripMenuItem.Text = "Dados"
        ' 
        ' ClientesToolStripMenuItem
        ' 
        ClientesToolStripMenuItem.Name = "ClientesToolStripMenuItem"
        ClientesToolStripMenuItem.Size = New Size(116, 22)
        ClientesToolStripMenuItem.Text = "Clientes"
        ' 
        ' MenuToolStripMenuItem1
        ' 
        MenuToolStripMenuItem1.DropDownItems.AddRange(New ToolStripItem() {MenuToolStripMenuItem2})
        MenuToolStripMenuItem1.Name = "MenuToolStripMenuItem1"
        MenuToolStripMenuItem1.Size = New Size(50, 20)
        MenuToolStripMenuItem1.Text = "Menu"
        ' 
        ' MenuToolStripMenuItem2
        ' 
        MenuToolStripMenuItem2.Name = "MenuToolStripMenuItem2"
        MenuToolStripMenuItem2.Size = New Size(151, 22)
        MenuToolStripMenuItem2.Text = "Ir para o Menu"
        ' 
        ' Aprovacao
        ' 
        AutoScaleDimensions = New SizeF(8F, 20F)
        AutoScaleMode = AutoScaleMode.Font
        ClientSize = New Size(1793, 811)
        Controls.Add(lblStatus)
        Controls.Add(btnCancelar)
        Controls.Add(btnAprovar)
        Controls.Add(dgvPedidosPendentes)
        Controls.Add(MenuStrip1)
        Font = New Font("Arial Narrow", 12F, FontStyle.Regular, GraphicsUnit.Point, CByte(0))
        MainMenuStrip = MenuStrip1
        Margin = New Padding(3, 4, 3, 4)
        Name = "Aprovacao"
        StartPosition = FormStartPosition.CenterScreen
        Text = "Aprovacao de Pedidos"
        WindowState = FormWindowState.Maximized
        CType(dgvPedidosPendentes, ComponentModel.ISupportInitialize).EndInit()
        MenuStrip1.ResumeLayout(False)
        MenuStrip1.PerformLayout()
        ResumeLayout(False)
        PerformLayout()
    End Sub

    Friend WithEvents dgvPedidosPendentes As DataGridView
    Friend WithEvents btnAprovar As Button
    Friend WithEvents btnCancelar As Button
    Friend WithEvents lblStatus As Label
    Friend WithEvents MenuStrip1 As MenuStrip
    Friend WithEvents MenuToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents SairToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents DashboardToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents GraficosToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents VisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ListaToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents MenuToolStripMenuItem1 As ToolStripMenuItem
    Friend WithEvents MenuToolStripMenuItem2 As ToolStripMenuItem
    Friend WithEvents GraficoTotalVisitantesToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents Id As DataGridViewTextBoxColumn
    Friend WithEvents Nome As DataGridViewTextBoxColumn
    Friend WithEvents Empresa As DataGridViewTextBoxColumn
    Friend WithEvents Telefone As DataGridViewTextBoxColumn
    Friend WithEvents Email As DataGridViewTextBoxColumn
    Friend WithEvents Data As DataGridViewTextBoxColumn
    Friend WithEvents ListaComFotoToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents DadosToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ClientesToolStripMenuItem As ToolStripMenuItem

End Class
