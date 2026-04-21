const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak, LevelFormat,
  TableOfContents
} = require('docx');
const fs = require('fs');

// ── Colour constants ──────────────────────────────────────────────────────────
const DARK_BLUE   = "1F3864";
const LIGHT_BLUE  = "D5E8F0";
const LIGHT_GREY  = "F2F2F2";
const WHITE       = "FFFFFF";

// ── Page dimensions (A4 in DXA) ───────────────────────────────────────────────
const PAGE_W      = 11906;
const PAGE_H      = 16838;
const MARGIN      = 1440;
const CONTENT_W   = PAGE_W - MARGIN * 2;   // 9026

// ── Border helper ─────────────────────────────────────────────────────────────
const thinBorder  = (color = "AAAAAA") => ({ style: BorderStyle.SINGLE, size: 4, color });
const cellBorders = (color = "AAAAAA") => ({
  top: thinBorder(color), bottom: thinBorder(color),
  left: thinBorder(color), right: thinBorder(color)
});

// ── Cell margin helper ────────────────────────────────────────────────────────
const cellPad = { top: 100, bottom: 100, left: 150, right: 150 };

// ── Make a header cell ────────────────────────────────────────────────────────
function headerCell(text, widthDXA) {
  return new TableCell({
    width:    { size: widthDXA, type: WidthType.DXA },
    borders:  cellBorders("8AACBF"),
    shading:  { fill: DARK_BLUE, type: ShadingType.CLEAR },
    margins:  cellPad,
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, color: WHITE, font: "Arial", size: 20 })]
    })]
  });
}

// ── Make a data cell ──────────────────────────────────────────────────────────
function dataCell(text, widthDXA, shade = false, align = AlignmentType.LEFT) {
  return new TableCell({
    width:   { size: widthDXA, type: WidthType.DXA },
    borders: cellBorders("CCCCCC"),
    shading: shade ? { fill: LIGHT_GREY, type: ShadingType.CLEAR }
                   : { fill: WHITE,      type: ShadingType.CLEAR },
    margins: cellPad,
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: align,
      children: [new TextRun({ text, font: "Arial", size: 20 })]
    })]
  });
}

// ── Page-break paragraph ──────────────────────────────────────────────────────
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ── Heading helper ────────────────────────────────────────────────────────────
function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, font: "Arial", size: 32, bold: true, color: DARK_BLUE })]
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, font: "Arial", size: 26, bold: true, color: DARK_BLUE })]
  });
}

// ── Body paragraph helper ─────────────────────────────────────────────────────
function body(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120 },
    children: [new TextRun({
      text, font: "Arial", size: 20,
      bold: opts.bold || false,
      italics: opts.italic || false,
    })]
  });
}

// ── Spacer ────────────────────────────────────────────────────────────────────
function spacer() {
  return new Paragraph({ spacing: { after: 80 }, children: [new TextRun("")] });
}

// ─────────────────────────────────────────────────────────────────────────────
// SECTION 3 — Scoring rules table
// columns: Horas Registadas | Resultado | Pontos | Motivo
// widths sum to CONTENT_W = 9026
// ─────────────────────────────────────────────────────────────────────────────
const col3 = [2506, 1800, 1400, 3320]; // sum = 9026

const scoringRows = [
  ["Menos de 7,2h",              "Negativo", "-1", "Saiu mais cedo"],
  ["Entre 7,2h e 9,2h",          "Positivo", "+1", "Cumpriu o horario"],
  ["Mais de 9,2h",               "Negativo", "-1", "Logout esquecido"],
  ["Sem registo de saida",        "Negativo", "-1", "Nao fez logout"],
  ["Sem registo no dia",          "Neutro",   "0",  "Folga ou ausencia"],
  ["Feriado / Fim de semana",     "\u2014",   "0",  "Nao contabilizado"],
];

const scoringTable = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: col3,
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        headerCell("Horas Registadas", col3[0]),
        headerCell("Resultado",        col3[1]),
        headerCell("Pontos",           col3[2]),
        headerCell("Motivo",           col3[3]),
      ]
    }),
    ...scoringRows.map((row, i) => new TableRow({
      children: row.map((cell, ci) => dataCell(cell, col3[ci], i % 2 === 1,
        ci === 2 ? AlignmentType.CENTER : AlignmentType.LEFT))
    }))
  ]
});

// ─────────────────────────────────────────────────────────────────────────────
// SECTION 9 — Access table
// columns: Perfil | URL | Descricao
// ─────────────────────────────────────────────────────────────────────────────
const col9 = [2006, 3500, 3520]; // sum = 9026

const accessRows = [
  ["Ecra TV (publico)", "http://192.168.10.156:8003/tv",    "Leaderboard sem login"],
  ["Colaborador",       "http://192.168.10.156:8003/login", "Pontuacao pessoal e loja"],
  ["Administrador",     "http://192.168.10.156:8003/login", "Acesso total ao painel"],
];

const accessTable = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: col9,
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        headerCell("Perfil",    col9[0]),
        headerCell("URL",       col9[1]),
        headerCell("Descricao", col9[2]),
      ]
    }),
    ...accessRows.map((row, i) => new TableRow({
      children: row.map((cell, ci) => dataCell(cell, col9[ci], i % 2 === 1))
    }))
  ]
});

// ─────────────────────────────────────────────────────────────────────────────
// SECTION 10 — Summary thresholds table
// columns: Parametro | Valor
// ─────────────────────────────────────────────────────────────────────────────
const col10 = [5426, 3600]; // sum = 9026

const summaryRows = [
  ["Horario minimo para ponto positivo", "7,2 horas (7h 12min)"],
  ["Horario maximo antes de penalizacao", "9,2 horas (9h 12min)"],
  ["Bonus semanal",                       "5 dias com +1 = +1 extra"],
  ["Feriado municipal Alcobaca",          "20 de Agosto"],
];

const summaryTable = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: col10,
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        headerCell("Parametro", col10[0]),
        headerCell("Valor",     col10[1]),
      ]
    }),
    ...summaryRows.map((row, i) => new TableRow({
      children: row.map((cell, ci) => dataCell(cell, col10[ci], i % 2 === 1))
    }))
  ]
});

// ─────────────────────────────────────────────────────────────────────────────
// DOCUMENT
// ─────────────────────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }
    ]
  },

  styles: {
    default: {
      document: { run: { font: "Arial", size: 20 } }
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1",
        basedOn: "Normal", next: "Normal", quickFormat: true,
        run:       { size: 32, bold: true, font: "Arial", color: DARK_BLUE },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2",
        basedOn: "Normal", next: "Normal", quickFormat: true,
        run:       { size: 26, bold: true, font: "Arial", color: DARK_BLUE },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 }
      },
    ]
  },

  sections: [
    // ── TITLE PAGE ────────────────────────────────────────────────────────────
    {
      properties: {
        page: {
          size:   { width: PAGE_W, height: PAGE_H },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: DARK_BLUE, space: 1 } },
            children: [new TextRun({
              text: "JogoSocem \u2014 Sistema de Pontuacao de Assiduidade",
              font: "Arial", size: 18, color: DARK_BLUE
            })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 6, color: DARK_BLUE, space: 1 } },
            tabStops: [{ type: "right", position: 9026 }],
            children: [
              new TextRun({ text: "JogoSocem \u2014 Confidencial SOCEM", font: "Arial", size: 16, color: "666666" }),
              new TextRun({ text: "\t", font: "Arial", size: 16 }),
              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "666666" }),
            ]
          })]
        })
      },
      children: [
        // Vertical spacing before title
        new Paragraph({ spacing: { after: 2400 }, children: [new TextRun("")] }),

        // Main title
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 240 },
          children: [new TextRun({
            text: "JogoSocem",
            font: "Arial", size: 72, bold: true, color: DARK_BLUE
          })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 480 },
          children: [new TextRun({
            text: "Sistema de Pontuacao de Assiduidade",
            font: "Arial", size: 40, color: DARK_BLUE
          })]
        }),

        // Subtitle
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 240 },
          children: [new TextRun({
            text: "Manual de Apresentacao para Chefias",
            font: "Arial", size: 28, bold: true, color: "444444"
          })]
        }),

        // Date
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 480 },
          children: [new TextRun({
            text: "Abril 2026",
            font: "Arial", size: 24, italics: true, color: "666666"
          })]
        }),

        // Horizontal rule via paragraph border
        new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: DARK_BLUE, space: 1 } },
          spacing: { after: 480 },
          children: [new TextRun("")]
        }),
      ]
    },

    // ── TABLE OF CONTENTS ─────────────────────────────────────────────────────
    {
      properties: {
        page: {
          size:   { width: PAGE_W, height: PAGE_H },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: DARK_BLUE, space: 1 } },
            children: [new TextRun({
              text: "JogoSocem \u2014 Sistema de Pontuacao de Assiduidade",
              font: "Arial", size: 18, color: DARK_BLUE
            })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 6, color: DARK_BLUE, space: 1 } },
            tabStops: [{ type: "right", position: 9026 }],
            children: [
              new TextRun({ text: "JogoSocem \u2014 Confidencial SOCEM", font: "Arial", size: 16, color: "666666" }),
              new TextRun({ text: "\t", font: "Arial", size: 16 }),
              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "666666" }),
            ]
          })]
        })
      },
      children: [
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun({ text: "Indice", font: "Arial", size: 32, bold: true, color: DARK_BLUE })]
        }),
        spacer(),
        new TableOfContents("Indice", { hyperlink: true, headingStyleRange: "1-2" }),
        pageBreak(),
      ]
    },

    // ── MAIN CONTENT ──────────────────────────────────────────────────────────
    {
      properties: {
        page: {
          size:   { width: PAGE_W, height: PAGE_H },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: DARK_BLUE, space: 1 } },
            children: [new TextRun({
              text: "JogoSocem \u2014 Sistema de Pontuacao de Assiduidade",
              font: "Arial", size: 18, color: DARK_BLUE
            })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 6, color: DARK_BLUE, space: 1 } },
            tabStops: [{ type: "right", position: 9026 }],
            children: [
              new TextRun({ text: "JogoSocem \u2014 Confidencial SOCEM", font: "Arial", size: 16, color: "666666" }),
              new TextRun({ text: "\t", font: "Arial", size: 16 }),
              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "666666" }),
            ]
          })]
        })
      },
      children: [

        // ── 1. INTRODUCAO ─────────────────────────────────────────────────────
        heading1("1. Introducao"),
        spacer(),
        body("O JogoSocem e um sistema de gamificacao que atribui automaticamente pontos diarios a cada colaborador com base nos registos de assiduidade do Sinex. O objetivo e promover a pontualidade, o cumprimento do horario e a presenca completa, tornando o desempenho visivel e comparavel entre equipas."),
        spacer(),
        pageBreak(),

        // ── 2. COMO FUNCIONA ──────────────────────────────────────────────────
        heading1("2. Como Funciona \u2014 Visao Geral"),
        spacer(),
        body("O sistema e composto por tres partes:"),
        spacer(),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { after: 80 },
          children: [
            new TextRun({ text: "Sinex (fonte de dados): ", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "sistema de producao onde os colaboradores fazem login/logout nas maquinas.", font: "Arial", size: 20 }),
          ]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { after: 80 },
          children: [
            new TextRun({ text: "Job Diario Automatico: ", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "todos os dias de manha, o sistema vai buscar automaticamente os registos do dia anterior ao Sinex e calcula os pontos.", font: "Arial", size: 20 }),
          ]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { after: 80 },
          children: [
            new TextRun({ text: "Aplicacao Web (JogoSocem): ", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "onde se visualizam os rankings, pontos individuais e a loja de premios.", font: "Arial", size: 20 }),
          ]
        }),
        spacer(),
        pageBreak(),

        // ── 3. REGRAS DE PONTUACAO ────────────────────────────────────────────
        heading1("3. Regras de Pontuacao Diaria"),
        spacer(),
        body("O sistema analisa as horas registadas por cada colaborador em cada dia util (segunda a sexta-feira, excluindo feriados nacionais e o feriado municipal de Alcobaca a 20 de agosto)."),
        spacer(),
        scoringTable,
        spacer(),
        new Paragraph({
          spacing: { after: 120 },
          children: [
            new TextRun({ text: "Bonus Semanal: ", font: "Arial", size: 20, bold: true, color: DARK_BLUE }),
            new TextRun({ text: "Se um colaborador tiver +1 em TODOS os dias uteis de uma semana (normalmente 5 dias), recebe +1 ponto extra de bonus atribuido na segunda-feira seguinte.", font: "Arial", size: 20 }),
          ]
        }),
        spacer(),
        new Paragraph({
          spacing: { after: 120 },
          children: [
            new TextRun({ text: "Nota: ", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "O sistema soma as horas de TODAS as seccoes onde o colaborador registou trabalho no mesmo dia, garantindo equidade para quem roda entre departamentos.", font: "Arial", size: 20, italics: true }),
          ]
        }),
        spacer(),
        pageBreak(),

        // ── 4. IDENTIFICACAO DOS COLABORADORES ────────────────────────────────
        heading1("4. Identificacao dos Colaboradores"),
        spacer(),
        body("O sistema identifica cada colaborador de forma unica atraves do EmployeeID do Sinex (numero interno unico por pessoa), e nao apenas pelo nome. Isto evita erros em casos de colaboradores com o mesmo nome em departamentos diferentes."),
        spacer(),
        body("Quando um colaborador aparece pela primeira vez, o sistema cria automaticamente o seu registo com o departamento/seccao correto. Nao e necessaria configuracao manual."),
        spacer(),
        pageBreak(),

        // ── 5. PROTECAO CONTRA DUPLICADOS ─────────────────────────────────────
        heading1("5. Protecao Contra Duplicados"),
        spacer(),
        body("Cada dia e processado uma unica vez por colaborador. Se o job correr duas vezes no mesmo dia, os pontos nao sao atribuidos em duplicado \u2014 o sistema deteta e ignora registos ja processados."),
        spacer(),
        pageBreak(),

        // ── 6. FUNCIONALIDADES DA APLICACAO WEB ──────────────────────────────
        heading1("6. Funcionalidades da Aplicacao Web"),
        spacer(),

        heading2("6.1 Leaderboard \u2014 Ecra Publico / TV"),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "Disponivel sem necessidade de login (para ecra de TV na fabrica).", font: "Arial", size: 20 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "Mostra o ranking geral de todos os colaboradores.", font: "Arial", size: 20 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "Mostra rankings por departamento.", font: "Arial", size: 20 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "Atualiza automaticamente.", font: "Arial", size: 20 })] }),
        spacer(),

        heading2("6.2 Area do Colaborador"),
        body("Cada colaborador tem acesso a uma area pessoal (com login) onde pode ver:"),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "A sua pontuacao atual.", font: "Arial", size: 20 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "A sua posicao no ranking geral.", font: "Arial", size: 20 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "O historico dos ultimos eventos (pontos ganhos e perdidos).", font: "Arial", size: 20 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "A loja de premios para trocar pontos.", font: "Arial", size: 20 })] }),
        spacer(),

        heading2("6.3 Loja de Premios"),
        body("Os colaboradores podem trocar pontos acumulados por premios definidos pela empresa (ex: dias de folga, vale de refeicao, outros beneficios configuraveis)."),
        spacer(),

        heading2("6.4 Painel de Administracao"),
        body("Exclusivo para administradores, permite:"),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "Visualizacao completa de todos os colaboradores e pontuacoes.", font: "Arial", size: 20 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "Atribuicao manual de pontos (positivos ou negativos) com justificacao.", font: "Arial", size: 20 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "Reprocessamento de periodos anteriores.", font: "Arial", size: 20 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "Gestao de contas de utilizador (criar, alterar password, eliminar).", font: "Arial", size: 20 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text: "Exportacao de dados para Excel.", font: "Arial", size: 20 })] }),
        spacer(),
        pageBreak(),

        // ── 7. AGENDAMENTO AUTOMATICO ─────────────────────────────────────────
        heading1("7. Agendamento Automatico"),
        spacer(),
        body("O job corre automaticamente todos os dias uteis via Windows Task Scheduler:"),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 },
          children: [
            new TextRun({ text: "Terca a Sexta-feira: ", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "processa o dia anterior.", font: "Arial", size: 20 }),
          ]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 },
          children: [
            new TextRun({ text: "Segunda-feira: ", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "processa a sexta-feira anterior + calcula o bonus semanal.", font: "Arial", size: 20 }),
          ]
        }),
        spacer(),
        body("Nao e necessaria qualquer intervencao manual no dia-a-dia."),
        spacer(),
        pageBreak(),

        // ── 8. CASOS ESPECIAIS ────────────────────────────────────────────────
        heading1("8. Casos Especiais"),
        spacer(),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 },
          children: [
            new TextRun({ text: "Colaborador sem registo num dia: ", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "0 pontos (neutro, nao penalizado).", font: "Arial", size: 20 }),
          ]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 },
          children: [
            new TextRun({ text: "Colaborador em multiplas seccoes no mesmo dia: ", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "horas somam-se para o calculo.", font: "Arial", size: 20 }),
          ]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 },
          children: [
            new TextRun({ text: "Feriados e fins de semana: ", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "nao sao contabilizados.", font: "Arial", size: 20 }),
          ]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 },
          children: [
            new TextRun({ text: "Colaborador novo no Sinex: ", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "criado automaticamente no JogoSocem na primeira aparicao.", font: "Arial", size: 20 }),
          ]
        }),
        spacer(),
        pageBreak(),

        // ── 9. ACESSO AO SISTEMA ──────────────────────────────────────────────
        heading1("9. Acesso ao Sistema"),
        spacer(),
        accessTable,
        spacer(),
        pageBreak(),

        // ── 10. RESUMO DOS LIMIARES ───────────────────────────────────────────
        heading1("10. Resumo dos Limiares"),
        spacer(),
        summaryTable,
        spacer(),
      ]
    }
  ]
});

// ── Write file ────────────────────────────────────────────────────────────────
const OUTPUT = "C:\\Users\\vitor.leonardo\\source\\repos\\Projetos_Claude\\JogoSocem\\Manual_JogoSocem.docx";

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUTPUT, buffer);
  console.log("Document written to:", OUTPUT);
}).catch(err => {
  console.error("Error generating document:", err);
  process.exit(1);
});
