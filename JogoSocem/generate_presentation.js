const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "SOCEM";
pres.title = "JogoSocem — Sistema de Pontuação de Assiduidade";

// Color palette
const C = {
  navyDark: "1F3864",
  navyMed: "2E75B6",
  iceBlue: "D5E8F0",
  white: "FFFFFF",
  lightGrey: "F2F2F2",
  darkText: "1A1A2E",
  lightRed: "FFCCCC",
  lightGreen: "CCFFCC",
};

// ─── SLIDE 1: Title ───────────────────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.navyDark };

  slide.addText("JogoSocem", {
    x: 0.5, y: 1.2, w: 9, h: 1.4,
    fontSize: 54, bold: true, color: C.white,
    align: "center", valign: "middle",
    fontFace: "Calibri",
  });

  slide.addText("Sistema de Pontuação de Assiduidade", {
    x: 0.5, y: 2.7, w: 9, h: 0.7,
    fontSize: 28, color: C.white,
    align: "center", valign: "middle",
    fontFace: "Calibri",
  });

  slide.addText("Apresentação às Chefias — Abril 2026", {
    x: 0.5, y: 4.6, w: 9, h: 0.5,
    fontSize: 18, color: C.iceBlue,
    align: "center", valign: "middle",
    fontFace: "Calibri",
  });
}

// ─── SLIDE 2: O que é o JogoSocem? ───────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("O que é o JogoSocem?", {
    x: 0.5, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  // Horizontal line under title
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  slide.addText([
    { text: "Sistema de gamificação de assiduidade e pontualidade", options: { bullet: true, breakLine: true } },
    { text: "Atribui pontos automaticamente a cada colaborador, todos os dias", options: { bullet: true, breakLine: true } },
    { text: "Dados retirados diretamente do Sinex (sem intervenção manual)", options: { bullet: true, breakLine: true } },
    { text: "Objetivo: promover o cumprimento do horário e tornar o desempenho visível", options: { bullet: true } },
  ], {
    x: 0.7, y: 1.3, w: 8.6, h: 3.8,
    fontSize: 16, color: C.darkText,
    fontFace: "Calibri", valign: "top",
    paraSpaceAfter: 14,
  });
}

// ─── SLIDE 3: Como Funciona ────────────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("Como Funciona", {
    x: 0.5, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  const boxes = [
    { header: "SINEX", body: "Fonte de dados: registos de login/logout dos colaboradores nas máquinas" },
    { header: "JOB DIÁRIO", body: "Todos os dias de manhã, o sistema calcula automaticamente os pontos do dia anterior" },
    { header: "APLICAÇÃO WEB", body: "Rankings, pontuações individuais, loja de prémios e painel de administração" },
  ];

  const boxW = 2.8;
  const boxH = 2.6;
  const startX = 0.55;
  const gapX = 0.25;
  const bodyY = 1.5;

  boxes.forEach((b, i) => {
    const x = startX + i * (boxW + gapX);

    // Header
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y: bodyY, w: boxW, h: 0.55,
      fill: { color: C.navyMed }, line: { color: C.navyMed },
    });
    slide.addText(b.header, {
      x, y: bodyY, w: boxW, h: 0.55,
      fontSize: 15, bold: true, color: C.white,
      align: "center", valign: "middle", fontFace: "Calibri",
      margin: 0,
    });

    // Body
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y: bodyY + 0.55, w: boxW, h: boxH - 0.55,
      fill: { color: C.lightGrey }, line: { color: "CCCCCC", width: 1 },
    });
    slide.addText(b.body, {
      x: x + 0.1, y: bodyY + 0.65, w: boxW - 0.2, h: boxH - 0.65,
      fontSize: 14, color: C.darkText,
      align: "center", valign: "top", fontFace: "Calibri",
      wrap: true,
    });
  });
}

// ─── SLIDE 4: Regras de Pontuação ─────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("Regras de Pontuação Diária", {
    x: 0.5, y: 0.25, w: 9, h: 0.65,
    fontSize: 36, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 0.93, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  const headerCell = (text) => ({
    text,
    options: { bold: true, color: C.white, fill: { color: C.navyDark }, fontSize: 13, align: "center", fontFace: "Calibri" },
  });

  const cell = (text, bg, align = "center") => ({
    text,
    options: { color: C.darkText, fill: { color: bg || C.white }, fontSize: 13, align, fontFace: "Calibri" },
  });

  const tableData = [
    [headerCell("Horas Registadas"), headerCell("Pontos"), headerCell("Resultado"), headerCell("Motivo")],
    [cell("< 7,2 horas", C.lightRed), cell("-1", C.lightRed), cell("Negativo", C.lightRed), cell("Saiu mais cedo", C.lightRed, "left")],
    [cell("7,2h a 9,2h", C.lightGreen), cell("+1", C.lightGreen), cell("Positivo", C.lightGreen), cell("Cumpriu o horário", C.lightGreen, "left")],
    [cell("> 9,2 horas", C.lightRed), cell("-1", C.lightRed), cell("Negativo", C.lightRed), cell("Logout esquecido", C.lightRed, "left")],
    [cell("Sem registo de saída", C.lightRed), cell("-1", C.lightRed), cell("Negativo", C.lightRed), cell("Não fez logout", C.lightRed, "left")],
    [cell("Sem registo no dia", C.white), cell("0", C.white), cell("Neutro", C.white), cell("Folga / ausência", C.white, "left")],
  ];

  slide.addTable(tableData, {
    x: 0.5, y: 1.1, w: 9,
    rowH: 0.52,
    border: { pt: 1, color: "CCCCCC" },
    colW: [2.5, 1.2, 1.6, 3.7],
  });

  slide.addText("Feriados e fins de semana não são contabilizados", {
    x: 0.5, y: 4.5, w: 9, h: 0.4,
    fontSize: 12, italic: true, color: "888888",
    align: "center", fontFace: "Calibri",
  });
}

// ─── SLIDE 5: Bónus Semanal ───────────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("Bónus Semanal", {
    x: 0.5, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  // Callout box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 2.2, y: 1.2, w: 5.6, h: 1.5,
    fill: { color: C.iceBlue }, line: { color: C.navyDark, width: 2 },
  });

  slide.addText("+1 Ponto Extra", {
    x: 2.2, y: 1.25, w: 5.6, h: 0.75,
    fontSize: 30, bold: true, color: C.navyMed,
    align: "center", valign: "middle", fontFace: "Calibri",
  });

  slide.addText("Se todos os dias úteis da semana forem +1", {
    x: 2.2, y: 2.0, w: 5.6, h: 0.55,
    fontSize: 15, color: C.navyDark,
    align: "center", valign: "middle", fontFace: "Calibri",
  });

  slide.addText([
    { text: "Semana completa: Segunda a Sexta, todos com +1", options: { bullet: true, breakLine: true } },
    { text: "Bónus atribuído automaticamente na segunda-feira seguinte", options: { bullet: true, breakLine: true } },
    { text: "Exemplo: 5 dias × +1 = 5 pontos + 1 bónus = 6 pontos na semana", options: { bullet: true, breakLine: true } },
    { text: "Incentivo ao cumprimento consistente", options: { bullet: true } },
  ], {
    x: 0.7, y: 2.85, w: 8.6, h: 2.4,
    fontSize: 16, color: C.darkText,
    fontFace: "Calibri", valign: "top",
    paraSpaceAfter: 10,
  });
}

// ─── SLIDE 6: Identificação dos Colaboradores ─────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("Identificação dos Colaboradores", {
    x: 0.5, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  slide.addText([
    { text: "Cada colaborador identificado pelo EmployeeID único do Sinex", options: { bullet: true, breakLine: true } },
    { text: "Sem confusão entre colaboradores com o mesmo nome", options: { bullet: true, breakLine: true } },
    { text: "Colaboradores em múltiplas secções: horas somam-se automaticamente", options: { bullet: true, breakLine: true } },
    { text: "Novos colaboradores criados automaticamente no primeiro registo", options: { bullet: true } },
  ], {
    x: 0.7, y: 1.3, w: 8.6, h: 3.8,
    fontSize: 16, color: C.darkText,
    fontFace: "Calibri", valign: "top",
    paraSpaceAfter: 14,
  });
}

// ─── SLIDE 7: Leaderboard ─────────────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("Leaderboard — Ecrã Público", {
    x: 0.5, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  slide.addText([
    { text: "Visível em TV na fábrica, sem necessidade de login", options: { bullet: true, breakLine: true } },
    { text: "Ranking geral de todos os colaboradores", options: { bullet: true, breakLine: true } },
    { text: "Rankings por departamento", options: { bullet: true, breakLine: true } },
    { text: "Atualização automática em tempo real", options: { bullet: true } },
  ], {
    x: 0.7, y: 1.3, w: 8.6, h: 3.8,
    fontSize: 16, color: C.darkText,
    fontFace: "Calibri", valign: "top",
    paraSpaceAfter: 14,
  });
}

// ─── SLIDE 8: Área do Colaborador & Loja ─────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("Área do Colaborador & Loja de Prémios", {
    x: 0.5, y: 0.3, w: 9, h: 0.7,
    fontSize: 32, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  // Left column
  const colW = 4.2;
  const colH = 3.4;
  const leftX = 0.5;
  const rightX = 5.3;
  const colY = 1.2;

  // Left header
  slide.addShape(pres.shapes.RECTANGLE, {
    x: leftX, y: colY, w: colW, h: 0.55,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });
  slide.addText("Área Pessoal", {
    x: leftX, y: colY, w: colW, h: 0.55,
    fontSize: 16, bold: true, color: C.white,
    align: "center", valign: "middle", fontFace: "Calibri", margin: 0,
  });

  // Left body bg
  slide.addShape(pres.shapes.RECTANGLE, {
    x: leftX, y: colY + 0.55, w: colW, h: colH - 0.55,
    fill: { color: C.lightGrey }, line: { color: "CCCCCC", width: 1 },
  });

  slide.addText([
    { text: "Login individual para cada colaborador", options: { bullet: true, breakLine: true } },
    { text: "Ver pontuação atual e posição no ranking", options: { bullet: true, breakLine: true } },
    { text: "Histórico de pontos ganhos e perdidos", options: { bullet: true } },
  ], {
    x: leftX + 0.15, y: colY + 0.65, w: colW - 0.3, h: colH - 0.75,
    fontSize: 14, color: C.darkText, fontFace: "Calibri",
    valign: "top", paraSpaceAfter: 10,
  });

  // Right header
  slide.addShape(pres.shapes.RECTANGLE, {
    x: rightX, y: colY, w: colW, h: 0.55,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });
  slide.addText("Loja de Prémios", {
    x: rightX, y: colY, w: colW, h: 0.55,
    fontSize: 16, bold: true, color: C.white,
    align: "center", valign: "middle", fontFace: "Calibri", margin: 0,
  });

  // Right body bg
  slide.addShape(pres.shapes.RECTANGLE, {
    x: rightX, y: colY + 0.55, w: colW, h: colH - 0.55,
    fill: { color: C.lightGrey }, line: { color: "CCCCCC", width: 1 },
  });

  slide.addText([
    { text: "Troca de pontos por prémios", options: { bullet: true, breakLine: true } },
    { text: "Exemplos: dias de folga, vales de refeição", options: { bullet: true, breakLine: true } },
    { text: "Prémios configuráveis pela empresa", options: { bullet: true } },
  ], {
    x: rightX + 0.15, y: colY + 0.65, w: colW - 0.3, h: colH - 0.75,
    fontSize: 14, color: C.darkText, fontFace: "Calibri",
    valign: "top", paraSpaceAfter: 10,
  });
}

// ─── SLIDE 9: Painel de Administração ─────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("Painel de Administração", {
    x: 0.5, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  slide.addText("Exclusivo para Administradores", {
    x: 0.5, y: 1.15, w: 9, h: 0.4,
    fontSize: 16, italic: true, color: C.navyMed,
    align: "left", fontFace: "Calibri",
  });

  slide.addText([
    { text: "Visualização completa de todos os colaboradores", options: { bullet: true, breakLine: true } },
    { text: "Atribuição manual de pontos (com justificação)", options: { bullet: true, breakLine: true } },
    { text: "Reprocessamento de períodos anteriores", options: { bullet: true, breakLine: true } },
    { text: "Gestão de contas de utilizador", options: { bullet: true, breakLine: true } },
    { text: "Exportação de dados para Excel", options: { bullet: true } },
  ], {
    x: 0.7, y: 1.65, w: 8.6, h: 3.5,
    fontSize: 16, color: C.darkText,
    fontFace: "Calibri", valign: "top",
    paraSpaceAfter: 10,
  });
}

// ─── SLIDE 10: Totalmente Automático ─────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("Totalmente Automático", {
    x: 0.5, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  const rows = [
    { label: "Terça a Sexta", desc: "Processa o dia anterior" },
    { label: "Segunda-feira", desc: "Processa sexta-feira + calcula bónus semanal" },
    { label: "Feriados / Fim de semana", desc: "Sistema não corre" },
  ];

  const rowH = 0.75;
  const startY = 1.25;
  const labelW = 3.2;
  const arrowW = 0.5;
  const descW = 5.3;
  const totalW = labelW + arrowW + descW;
  const startX = (10 - totalW) / 2;

  rows.forEach((r, i) => {
    const y = startY + i * (rowH + 0.15);
    const isAlt = i % 2 === 0;

    // Label box
    slide.addShape(pres.shapes.RECTANGLE, {
      x: startX, y, w: labelW, h: rowH,
      fill: { color: C.navyDark }, line: { color: C.navyDark },
    });
    slide.addText(r.label, {
      x: startX, y, w: labelW, h: rowH,
      fontSize: 15, bold: true, color: C.white,
      align: "center", valign: "middle", fontFace: "Calibri", margin: 0,
    });

    // Arrow text
    slide.addText("→", {
      x: startX + labelW, y, w: arrowW, h: rowH,
      fontSize: 20, color: C.navyMed,
      align: "center", valign: "middle", fontFace: "Calibri",
    });

    // Desc box
    slide.addShape(pres.shapes.RECTANGLE, {
      x: startX + labelW + arrowW, y, w: descW, h: rowH,
      fill: { color: isAlt ? C.iceBlue : C.lightGrey }, line: { color: "CCCCCC", width: 1 },
    });
    slide.addText(r.desc, {
      x: startX + labelW + arrowW + 0.1, y, w: descW - 0.2, h: rowH,
      fontSize: 15, color: C.darkText,
      align: "left", valign: "middle", fontFace: "Calibri",
    });
  });

  slide.addText("Nenhuma intervenção manual necessária no dia-a-dia", {
    x: 0.5, y: 4.9, w: 9, h: 0.45,
    fontSize: 14, italic: true, color: "888888",
    align: "center", fontFace: "Calibri",
  });
}

// ─── SLIDE 11: Como Aceder ────────────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("Como Aceder", {
    x: 0.5, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  const headerCell = (text) => ({
    text,
    options: { bold: true, color: C.white, fill: { color: C.navyDark }, fontSize: 14, align: "center", fontFace: "Calibri" },
  });

  const cell = (text, align = "center") => ({
    text,
    options: { color: C.darkText, fill: { color: C.white }, fontSize: 13, align, fontFace: "Calibri" },
  });

  const altCell = (text, align = "center") => ({
    text,
    options: { color: C.darkText, fill: { color: C.lightGrey }, fontSize: 13, align, fontFace: "Calibri" },
  });

  const tableData = [
    [headerCell("Perfil"), headerCell("Endereço"), headerCell("Acesso")],
    [cell("Ecrã TV (público)"), cell("http://192.168.10.156:8003/tv"), cell("Sem login necessário")],
    [altCell("Colaborador"), altCell("http://192.168.10.156:8003/login"), altCell("Login individual")],
    [cell("Administrador"), cell("http://192.168.10.156:8003/login"), cell("Acesso total ao painel")],
  ];

  slide.addTable(tableData, {
    x: 0.5, y: 1.25, w: 9,
    rowH: 0.7,
    border: { pt: 1, color: "CCCCCC" },
    colW: [2.0, 4.5, 2.5],
  });
}

// ─── SLIDE 12: Em Resumo ──────────────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addText("Em Resumo", {
    x: 0.5, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, bold: true, color: C.navyDark,
    align: "left", fontFace: "Calibri",
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.05, w: 9, h: 0.04,
    fill: { color: C.navyMed }, line: { color: C.navyMed },
  });

  const points = [
    { keyword: "100% Automático", desc: " — sem trabalho manual diário" },
    { keyword: "Dados em Tempo Real", desc: " — diretamente do Sinex, sempre atualizados" },
    { keyword: "Transparente", desc: " — cada colaborador vê a sua pontuação" },
    { keyword: "Justo", desc: " — regras claras e iguais para todos" },
    { keyword: "Configurável", desc: " — prémios e regras adaptáveis às necessidades" },
  ];

  const bulletItems = points.map((p, i) => {
    const isLast = i === points.length - 1;
    return {
      text: [
        { text: p.keyword, options: { bold: true } },
        { text: p.desc },
      ],
      options: { bullet: true, breakLine: !isLast },
    };
  });

  // pptxgenjs doesn't support mixed text inside bullet arrays this way,
  // so we render each as a separate text element
  points.forEach((p, i) => {
    const y = 1.3 + i * 0.75;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y: y - 0.05, w: 9, h: 0.65,
      fill: { color: i % 2 === 0 ? C.lightGrey : C.white }, line: { color: "DDDDDD", width: 1 },
    });
    slide.addText([
      { text: p.keyword, options: { bold: true, color: C.navyMed } },
      { text: p.desc, options: { color: C.darkText } },
    ], {
      x: 0.65, y: y - 0.05, w: 8.7, h: 0.65,
      fontSize: 16, fontFace: "Calibri",
      valign: "middle",
    });
  });
}

// ─── SLIDE 13: Final ──────────────────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: C.navyDark };

  slide.addText("Obrigado", {
    x: 0.5, y: 1.4, w: 9, h: 1.4,
    fontSize: 54, bold: true, color: C.white,
    align: "center", valign: "middle", fontFace: "Calibri",
  });

  slide.addText("Questões?", {
    x: 0.5, y: 3.0, w: 9, h: 0.7,
    fontSize: 28, color: C.iceBlue,
    align: "center", valign: "middle", fontFace: "Calibri",
  });

  slide.addText("JogoSocem — SOCEM, Abril 2026", {
    x: 0.5, y: 4.7, w: 9, h: 0.45,
    fontSize: 16, color: C.white,
    align: "center", valign: "middle", fontFace: "Calibri",
  });
}

// Save
pres.writeFile({ fileName: "C:\\Users\\vitor.leonardo\\source\\repos\\Projetos_Claude\\JogoSocem\\Apresentacao_JogoSocem.pptx" })
  .then(() => console.log("✅ Presentation saved successfully!"))
  .catch((err) => { console.error("❌ Error:", err); process.exit(1); });
