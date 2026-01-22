const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle, 
        WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// Color scheme
const COLORS = {
  primary: "1B4F72",
  secondary: "2874A6",
  accent: "E67E22",
  text: "2C3E50",
  lightBg: "EBF5FB",
  instructorBg: "FEF9E7",
  warningBg: "FDEDEC"
};

// Table border style
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "BDC3C7" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: COLORS.primary, font: "Calibri Light" },
        paragraph: { spacing: { before: 120, after: 240 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: COLORS.primary, font: "Calibri Light" },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: COLORS.secondary, font: "Calibri" },
        paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: COLORS.text, font: "Calibri" },
        paragraph: { spacing: { before: 200, after: 60 }, outlineLevel: 2 } },
      { id: "InstructorNote", name: "Instructor Note", basedOn: "Normal",
        run: { size: 20, italics: true, color: "7B7D7D" },
        paragraph: { spacing: { before: 60, after: 60 }, indent: { left: 360 } } },
      { id: "CodeBlock", name: "Code Block", basedOn: "Normal",
        run: { size: 18, font: "Consolas", color: "2E4053" },
        paragraph: { spacing: { before: 80, after: 80 } } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-1",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-2",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-3",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-4",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-5",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-6",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    properties: {
      page: { margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ 
        alignment: AlignmentType.RIGHT,
        children: [
          new TextRun({ text: "Rețele de Calculatoare — Săptămâna 5", size: 18, color: "7B7D7D" })
        ]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "Pagina ", size: 18 }), 
          new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
          new TextRun({ text: " din ", size: 18 }), 
          new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18 }),
          new TextRun({ text: " | ASE CSIE — Informatică Economică", size: 18, color: "7B7D7D" })
        ]
      })] })
    },
    children: [
      // ═══════════════════════════════════════════════════════════════════
      // COVER PAGE
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ spacing: { before: 2400 } }),
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("REȚELE DE CALCULATOARE")] }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER, spacing: { before: 240 },
        children: [new TextRun({ text: "Cursul 5 | Seminar 5 | Laborator 5", size: 32, color: COLORS.secondary })]
      }),
      new Paragraph({ spacing: { before: 480 } }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Nivelul Rețea: Adresare IPv4/IPv6, Subnetting, VLSM", size: 28, bold: true, color: COLORS.text })]
      }),
      new Paragraph({ spacing: { before: 960 } }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Anul universitar 2024–2025, Semestrul 2", size: 22, color: "7B7D7D" })]
      }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Academia de Studii Economice București", size: 22, color: "7B7D7D" })]
      }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Facultatea de Cibernetică, Statistică și Informatică Economică", size: 22, color: "7B7D7D" })]
      }),
      new Paragraph({ spacing: { before: 1440 } }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "📘 Notițe pentru cadre didactice și studenți", size: 20, italics: true, color: "7B7D7D" })]
      }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 1: SCOPUL SĂPTĂMÂNII
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Scopul Săptămânii")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Ce vom învăța")] }),
      new Paragraph({ children: [new TextRun("Această săptămână marchează tranziția de la nivelurile inferioare ale stivei TCP/IP către nivelul care asigură conectivitatea globală: nivelul rețea. Vom explora mecanismele prin care pachetele de date pot traversa granițele rețelelor locale și ajunge la destinații aflate oriunde pe Internet.")] }),
      new Paragraph({ spacing: { before: 120 } }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Structura adreselor IPv4 și IPv6: format, clase istorice, notație CIDR")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Calculul parametrilor rețelei: adresă de rețea, broadcast, interval de gazde valide")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Tehnici de partiționare: FLSM (subrețele egale) și VLSM (alocare optimizată)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Header-ul IPv4 vs IPv6: câmpuri esențiale și diferențe arhitecturale")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Simularea rutării într-un mediu virtual (Mininet): configurare, verificare, debugging")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("De ce contează")] }),
      new Paragraph({ children: [new TextRun("Adresarea IP reprezintă fundația oricărei comunicații pe Internet. Un programator care stăpânește aceste concepte poate:")] }),
      
      new Paragraph({ numbering: { reference: "numbered-1", level: 0 }, children: [new TextRun({ text: "Diagnostica probleme de conectivitate ", bold: true }), new TextRun("— înțelegerea subnetting-ului ajută la identificarea rapidă a problemelor de rutare sau izolare a traficului")] }),
      new Paragraph({ numbering: { reference: "numbered-1", level: 0 }, children: [new TextRun({ text: "Proiecta infrastructuri scalabile ", bold: true }), new TextRun("— planificarea corectă a spațiului de adrese previne epuizarea și conflictele")] }),
      new Paragraph({ numbering: { reference: "numbered-1", level: 0 }, children: [new TextRun({ text: "Automatiza deployment-uri cloud ", bold: true }), new TextRun("— VPC-urile AWS, Azure, GCP necesită configurarea explicită a CIDR-urilor")] }),
      new Paragraph({ numbering: { reference: "numbered-1", level: 0 }, children: [new TextRun({ text: "Securiza aplicațiile ", bold: true }), new TextRun("— segmentarea rețelei prin subrețele izolate reduce suprafața de atac")] }),
      
      new Paragraph({ spacing: { before: 200 }, style: "InstructorNote", children: [
        new TextRun({ text: "💡 Notă pentru cadru didactic: ", bold: true }),
        new TextRun("Subliniați conexiunea cu realitatea profesională — studenții vor întâlni aceste concepte la interviuri tehnice și în primele săptămâni de lucru. Pregătiți 2-3 exemple concrete din proiecte reale (e.g., configurarea unui VPC în AWS, debugging CIDR mismatch).")
      ] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 2: PRERECHIZITE ȘI RECAPITULARE
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Prerechizite și Recapitulare")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Din săptămânile anterioare")] }),
      
      new Table({
        columnWidths: [2500, 6500],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Săptămâna", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Concepte relevante pentru S5", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("S1–S2")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Modelele OSI și TCP/IP, încapsulare, PDU-uri")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("S3")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Programare socket: structuri sockaddr, AF_INET, bind()")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("S4")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Nivelul legătură de date: cadre Ethernet, adrese MAC")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("Recapitulare expresă: operații pe biți")] }),
      new Paragraph({ children: [new TextRun("Calculele CIDR se bazează pe operații pe biți. Asigurați-vă că stăpâniți:")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun({ text: "AND (&): ", bold: true }), new TextRun("extrage partea de rețea (IP & Mask = Network)")
      ] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun({ text: "OR (|): ", bold: true }), new TextRun("calculează broadcast-ul (Network | Wildcard = Broadcast)")
      ] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun({ text: "NOT (~): ", bold: true }), new TextRun("inversează masca pentru a obține wildcard mask")
      ] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("Tabel de conversie rapidă")] }),
      
      new Table({
        columnWidths: [1500, 2500, 2500, 2500],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Zecimal", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Binar", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Ca mască", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Prefix", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("255")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("11111111")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("8 biți rețea")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("/8 per octet")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("128")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("10000000")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("1 bit rețea")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Împarte în 2")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("192")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("11000000")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("2 biți rețea")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Împarte în 4")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("240")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("11110000")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("4 biți rețea")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Împarte în 16")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ spacing: { before: 240 }, style: "InstructorNote", children: [
        new TextRun({ text: "⏱️ Timing: ", bold: true }),
        new TextRun("Alocați maxim 10 minute pentru recapitulare. Dacă studenții au dificultăți cu conversiile, recomandați exerciții suplimentare acasă și continuați cu materia.")
      ] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 3: CURS
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Curs: Nivelul Rețea")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Rolul nivelului rețea")] }),
      new Paragraph({ children: [new TextRun("Nivelul rețea (Layer 3) asigură două funcții fundamentale:")] }),
      
      new Paragraph({ numbering: { reference: "numbered-2", level: 0 }, children: [
        new TextRun({ text: "Adresarea logică ", bold: true }), 
        new TextRun("— identificarea unică a fiecărui dispozitiv conectat la rețea prin adrese IP")
      ] }),
      new Paragraph({ numbering: { reference: "numbered-2", level: 0 }, children: [
        new TextRun({ text: "Rutarea ", bold: true }), 
        new TextRun("— determinarea căii optime pentru transmiterea pachetelor între rețele diferite")
      ] }),
      
      new Paragraph({ spacing: { before: 160 }, children: [
        new TextRun({ text: "Analogie: ", italics: true }),
        new TextRun("Daca adresa MAC este numarul de serie al unui telefon, adresa IP este numarul de telefon - poate fi schimbat, portat intre operatori si permite rutare ierarhica (prefix tara, prefix oras, numar local).")
      ] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Structura adreselor IPv4")] }),
      new Paragraph({ children: [new TextRun("O adresă IPv4 constă din 32 de biți, reprezentați în format \"dotted-decimal\" — patru numere zecimale (0–255) separate prin puncte.")] }),
      
      new Paragraph({ style: "CodeBlock", spacing: { before: 120 }, children: [new TextRun("Exemplu: 192.168.1.10 = 11000000.10101000.00000001.00001010")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Adrese speciale")] }),
      
      new Table({
        columnWidths: [2500, 4500, 2000],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Interval", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Scop", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "RFC", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("10.0.0.0/8")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Adrese private (rețele mari)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RFC 1918")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("172.16.0.0/12")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Adrese private (rețele medii)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RFC 1918")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("192.168.0.0/16")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Adrese private (rețele mici)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RFC 1918")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("127.0.0.0/8")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Loopback (localhost)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RFC 1122")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("169.254.0.0/16")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Link-local (APIPA)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RFC 3927")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 CIDR și Subnetting")] }),
      new Paragraph({ children: [new TextRun("CIDR (Classless Inter-Domain Routing) a înlocuit sistemul claselor, permițând prefixe de lungime variabilă.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Formule esențiale")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Total adrese = 2^(32 - prefix)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Hosturi valizi = 2^(32 - prefix) - 2")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Network address = IP AND subnet_mask")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Broadcast = IP OR wildcard_mask")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Exemplu rezolvat")] }),
      new Paragraph({ children: [new TextRun({ text: "Problemă: ", bold: true }), new TextRun("Analizați 172.16.50.12/21")] }),
      
      new Paragraph({ style: "CodeBlock", spacing: { before: 80 }, children: [new TextRun("Prefix /21 → Mască: 255.255.248.0")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("172.16.50.12 AND 255.255.248.0 = 172.16.48.0 (Network)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Broadcast: 172.16.55.255")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Hosturi: 172.16.48.1 — 172.16.55.254 (2046 adrese)")] }),
      
      new Paragraph({ spacing: { before: 200 }, style: "InstructorNote", children: [
        new TextRun({ text: "🎯 Mini-demo la curs: ", bold: true }),
        new TextRun("Rulați python/apps/subnet_calc.py cu adresa 172.16.50.12/21 și proiectați rezultatul. Explicați pas cu pas conversia binară.")
      ] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.4 FLSM vs VLSM")] }),
      
      new Table({
        columnWidths: [1500, 3750, 3750],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Aspect", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "FLSM", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "VLSM", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Descriere")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Toate subrețelele au același prefix")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Prefixe diferite, adaptate necesităților")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Eficiență")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Scăzută — risipă de adrese")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Ridicată — alocare optimizată")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Complexitate")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Simplă, ușor de planificat")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Necesită planificare atentă")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Utilizare")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Rețele uniforme, simple")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Rețele enterprise, cloud VPC")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.5 IPv6: De ce și cum")] }),
      new Paragraph({ children: [new TextRun("IPv6 rezolvă limitările IPv4 prin:")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Spațiu extins: ", bold: true }), new TextRun("128 biți = 3.4 × 10³⁸ adrese")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Header simplificat: ", bold: true }), new TextRun("mai puține câmpuri, procesare mai rapidă")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Auto-configurare (SLAAC): ", bold: true }), new TextRun("nu necesită DHCP pentru adresare")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Reguli de comprimare IPv6")] }),
      new Paragraph({ numbering: { reference: "numbered-3", level: 0 }, children: [new TextRun("Eliminarea zerourilor de început din fiecare grup")] }),
      new Paragraph({ numbering: { reference: "numbered-3", level: 0 }, children: [new TextRun("Înlocuirea unei secvențe continue de grupuri 0000 cu ::")] }),
      new Paragraph({ numbering: { reference: "numbered-3", level: 0 }, children: [new TextRun(":: poate fi folosit o singură dată per adresă")] }),
      
      new Paragraph({ style: "CodeBlock", spacing: { before: 120 }, children: [new TextRun("2001:0db8:0000:0000:0000:0000:0000:0001 → 2001:db8::1")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 4: SEMINAR
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Seminar: Ghid Practic")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Parcurs pas cu pas")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Partea A: Analiza CIDR cu Python")] }),
      new Paragraph({ children: [new TextRun({ text: "Timp estimat: ", italics: true }), new TextRun("15 minute")] }),
      
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Pas 1: ", bold: true }), new TextRun("Navigați în directorul exercițiilor")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("cd python/exercises")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Pas 2: ", bold: true }), new TextRun("Analizați o adresă CIDR")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("python ex_5_01_cidr_flsm.py analyze 172.16.50.12/21")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Rezultat așteptat: ", bold: true })] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Network: 172.16.48.0/21")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Netmask: 255.255.248.0")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Broadcast: 172.16.55.255")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Host range: 172.16.48.1 - 172.16.55.254")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("Valid hosts: 2046")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Partea B: Partiționare FLSM")] }),
      new Paragraph({ children: [new TextRun({ text: "Timp estimat: ", italics: true }), new TextRun("15 minute")] }),
      
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Scenariu: ", bold: true }), new TextRun("Împărțiți 10.0.0.0/8 în 4 subrețele egale")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("python ex_5_01_cidr_flsm.py flsm 10.0.0.0/8 4")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Interpretare: ", bold: true }), new TextRun("Fiecare subrețea primește 2³⁰ - 2 = 1.073.741.822 gazde. Prefixul crește de la /8 la /10 (adăugăm 2 biți pentru a distinge 4 subrețele).")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Partea C: Planificare VLSM")] }),
      new Paragraph({ children: [new TextRun({ text: "Timp estimat: ", italics: true }), new TextRun("20 minute")] }),
      
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Scenariu: ", bold: true }), new TextRun("Alocați 192.168.1.0/24 pentru departamente cu nevoi diferite: IT (50), HR (20), Finance (10), Management (5), legături WAN (2×2)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("python ex_5_02_vlsm_ipv6.py vlsm 192.168.1.0/24 50 20 10 5 2 2")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Principiu VLSM: ", bold: true }), new TextRun("Sortăm descrescător după numărul de gazde și alocăm de la cel mai mare la cel mai mic.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 Interpretarea rezultatelor")] }),
      new Paragraph({ children: [new TextRun("La fiecare pas, verificați:")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Adresa de rețea să fie corect calculată (biți de host = 0)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Broadcast-ul să fie ultimul din bloc")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Subrețelele să nu se suprapună")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Eficiența alocării (adrese utilizate vs disponibile)")] }),
      
      new Paragraph({ spacing: { before: 200 }, style: "InstructorNote", children: [
        new TextRun({ text: "⚠️ Greșeală frecventă: ", bold: true }),
        new TextRun("Studenții uită să scadă 2 din total pentru adresele de rețea și broadcast. Subliniați de ce prima și ultima adresă nu pot fi atribuite gazdelor.")
      ] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 5: LABORATOR
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Laborator Practic")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Experiment: Topologie Mininet cu rutare")] }),
      
      new Paragraph({ children: [new TextRun({ text: "Obiectiv: ", bold: true }), new TextRun("Construiți o rețea cu 2 subrețele și un router, apoi verificați conectivitatea.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Pas 0: Verificare mediu")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("make verify")] }),
      new Paragraph({ children: [new TextRun("Toate testele trebuie să treacă înainte de a continua.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Pas 1: Pornirea topologiei de bază")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("cd mininet")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sudo python3 topo_5_base.py")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Topologie: ", bold: true })] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("h1 (10.0.1.10/24) -- [s1] -- r1 -- [s2] -- h2 (10.0.2.10/24)")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Pas 2: Testare conectivitate")] }),
      new Paragraph({ children: [new TextRun("Din CLI-ul Mininet:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("mininet> h1 ping -c 3 h2")] }),
      
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Rezultat așteptat: ", bold: true }), new TextRun("0% packet loss")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Pas 3: Analiza rutelor")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("mininet> h1 ip route")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("mininet> r1 ip route")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 Experiment: VLSM cu topologie extinsă")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sudo python3 topo_5_extended.py")] }),
      new Paragraph({ children: [new TextRun("Această topologie include 3 subrețele cu prefixe diferite, demonstrând VLSM în practică.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.3 Extensii opționale")] }),
      
      new Paragraph({ numbering: { reference: "numbered-4", level: 0 }, children: [new TextRun({ text: "Captură pachete: ", bold: true }), new TextRun("mininet> h1 tcpdump -i h1-eth0 -c 10 -w /tmp/h1_capture.pcap &")] }),
      new Paragraph({ numbering: { reference: "numbered-4", level: 0 }, children: [new TextRun({ text: "Test debit: ", bold: true }), new TextRun("Rulați iperf între h1 și h2")] }),
      new Paragraph({ numbering: { reference: "numbered-4", level: 0 }, children: [new TextRun({ text: "IPv6 dual-stack: ", bold: true }), new TextRun("Adăugați adrese IPv6 și testați conectivitatea")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 6: GREȘELI FRECVENTE
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Greșeli Frecvente și Debugging")] }),
      
      new Table({
        columnWidths: [3000, 3000, 3000],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.warningBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Simptom", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.warningBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Cauză probabilă", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.warningBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Soluție", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("ping: Network unreachable")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Lipsă rută către destinație sau gateway incorect")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Verificați ip route și default gateway")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Subrețele se suprapun")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Greșeală la calculul prefixului sau alocării")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Recalculați de la zero, verificați suprapunerea")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("IP forwarding dezactivat")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Routerul nu transmite pachete între interfețe")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("sysctl net.ipv4.ip_forward=1")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Mininet nu pornește")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Resurse blocate de sesiune anterioară")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("make clean sau sudo mn -c")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Număr incorect de gazde")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Nu s-au scăzut adresele de rețea/broadcast")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Hosturi = 2^(32-prefix) - 2")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("Comenzi utile pentru debugging")] }),
      
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Verificare configurație IP")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("ip addr show")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Afișare tabel de rutare")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("ip route")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Captură live pachete ICMP")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sudo tcpdump -i any icmp -n")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Verificare IP forwarding")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sysctl net.ipv4.ip_forward")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 7: EXERCIȚII
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Exerciții de Consolidare")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul S5.1: Analiza CIDR (10 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerință: ", bold: true }), new TextRun("Pentru adresa 10.45.128.200/18, determinați:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Adresa de rețea și masca în format dotted-decimal")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Adresa de broadcast")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Intervalul de gazde valide și numărul lor")] }),
      new Paragraph({ children: [new TextRun({ text: "Verificare: ", italics: true }), new TextRun("python ex_5_01_cidr_flsm.py analyze 10.45.128.200/18")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul S5.2: Partiționare FLSM (10 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerință: ", bold: true }), new TextRun("Împărțiți 172.30.0.0/20 în 32 de subrețele egale. Listați primele 5 subrețele cu adresa de rețea, broadcast și interval gazde.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul S5.3: Planificare VLSM (15 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Scenariu: ", bold: true }), new TextRun("Compania TechCorp are sediu cu 4 departamente:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Development: 100 stații")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Sales: 45 stații")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("HR: 15 stații")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Server Room: 10 servere")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("2 legături WAN (câte 2 adrese fiecare)")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerință: ", bold: true }), new TextRun("Proiectați schema VLSM pornind de la 192.168.50.0/24. Calculați eficiența alocării.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul S5.4: Comprimare IPv6 (10 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerință: ", bold: true }), new TextRun("Comprimați la forma minimală:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("a) 2001:0db8:0000:0042:0000:0000:0000:8a2e")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("b) fe80:0000:0000:0000:0000:0000:0000:0001")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("c) 0000:0000:0000:0000:0000:ffff:c0a8:0164")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul S5.5: Expandare IPv6 (10 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerință: ", bold: true }), new TextRun("Expandați la forma completă:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("a) 2001:db8::1")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("b) fe80::1")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("c) ::ffff:192.168.1.100")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Exercițiul S5.6 — Challenge (15 puncte)")] }),
      new Paragraph({ children: [new TextRun({ text: "Scenariu avansat: ", bold: true }), new TextRun("O universitate primește blocul IPv6 2001:db8:acad::/48. Proiectați o schemă de adresare care să aloce:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Câte un /64 pentru fiecare din cele 8 facultăți")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("4 subrețele /64 pentru infrastructură (servere, management)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Rezervați 4 subrețele /64 pentru extindere viitoare")] }),
      new Paragraph({ children: [new TextRun({ text: "Cerință: ", bold: true }), new TextRun("Prezentați planul de alocare și justificați convențiile de numerotare.")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 8: REFLECȚIE
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Mini-Reflecție")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Ce am învățat")] }),
      new Paragraph({ children: [new TextRun("După parcurgerea acestei săptămâni, ar trebui să puteți răspunde la:")] }),
      
      new Paragraph({ numbering: { reference: "numbered-5", level: 0 }, children: [new TextRun("Care este diferența fundamentală dintre o adresă MAC și o adresă IP?")] }),
      new Paragraph({ numbering: { reference: "numbered-5", level: 0 }, children: [new TextRun("De ce folosim CIDR în loc de sistemul claselor?")] }),
      new Paragraph({ numbering: { reference: "numbered-5", level: 0 }, children: [new TextRun("Când este preferabil VLSM față de FLSM?")] }),
      new Paragraph({ numbering: { reference: "numbered-5", level: 0 }, children: [new TextRun("Care sunt principalele avantaje ale IPv6?")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Unde se folosește în practică")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Cloud computing: ", bold: true }), new TextRun("VPC design în AWS/Azure/GCP necesită planificare CIDR")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Containerizare: ", bold: true }), new TextRun("Kubernetes folosește subrețele pentru Pods și Services")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Securitate: ", bold: true }), new TextRun("Firewalls și ACL-uri operează pe prefixe CIDR")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "DevOps/IaC: ", bold: true }), new TextRun("Terraform, Ansible gestionează adrese IP programatic")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Legătura cu rolul de programator")] }),
      new Paragraph({ children: [new TextRun("Programarea de rețea modernă presupune configurarea corectă a bind addresses, înțelegerea NAT traversal și debugging-ul problemelor de conectivitate. Cunoașterea temeinică a adresării IP transformă un programator competent într-unul care poate lucra eficient cu infrastructură distribuită.")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 9: CONTRIBUȚIA LA PROIECT
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("9. Contribuția Săptămânii la Proiect")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Artefact livrabil")] }),
      new Paragraph({ children: [new TextRun({ text: "Deadline: ", bold: true }), new TextRun("Până la începutul săptămânii 6")] }),
      
      new Paragraph({ spacing: { before: 160 }, children: [new TextRun({ text: "Cerință pentru echipă: ", bold: true }), new TextRun("Adăugați la proiect o schemă de adresare care include:")] }),
      
      new Paragraph({ numbering: { reference: "numbered-6", level: 0 }, children: [new TextRun("Minimum 3 subrețele distincte (pot fi FLSM sau VLSM)")] }),
      new Paragraph({ numbering: { reference: "numbered-6", level: 0 }, children: [new TextRun("Justificarea alegerii prefixelor (de ce aceste mărimi?)")] }),
      new Paragraph({ numbering: { reference: "numbered-6", level: 0 }, children: [new TextRun("O diagramă de topologie (poate fi ASCII art sau imagine)")] }),
      new Paragraph({ numbering: { reference: "numbered-6", level: 0 }, children: [new TextRun("Opțional: script Mininet funcțional care demonstrează conectivitatea")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Criterii de evaluare")] }),
      
      new Table({
        columnWidths: [5000, 2000, 2000],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Criteriu", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Punctaj", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Bonus", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Schema conține minim 3 subrețele fără suprapunere")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("30%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("—")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Justificarea alegerilor este coerentă")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("25%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("—")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Topologia este clară și completă")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("25%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("—")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Script Mininet funcțional")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("20%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("+10%")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // ═══════════════════════════════════════════════════════════════════
      // SECTION 10: BIBLIOGRAFIE
      // ═══════════════════════════════════════════════════════════════════
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("10. Bibliografie și Resurse")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Lucrări cu DOI")] }),
      
      new Table({
        columnWidths: [500, 5500, 3000],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "#", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Referință", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "DOI", bold: true })] })] })
            ]
          }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("1")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Kurose, J. F., & Ross, K. W. (2017). Computer Networking: A Top-Down Approach (7th ed.). Pearson.")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "—", italics: true })] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("2")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Rhodes, B., & Goetzen, J. (2014). Foundations of Python Network Programming (3rd ed.). Apress.")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("10.1007/978-1-4302-5855-1")] })] })
          ] }),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Lantz, B., et al. (2010). A Network in a Laptop: Rapid Prototyping for SDN. HotNets.")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("10.1145/1868447.1868466")] })] })
          ] })
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("Standarde și specificații")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "RFC 791 ", bold: true }), new TextRun("— Internet Protocol (IPv4)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "RFC 1918 ", bold: true }), new TextRun("— Address Allocation for Private Internets")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "RFC 4291 ", bold: true }), new TextRun("— IP Version 6 Addressing Architecture")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "RFC 4632 ", bold: true }), new TextRun("— Classless Inter-Domain Routing (CIDR)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "RFC 8200 ", bold: true }), new TextRun("— Internet Protocol, Version 6 (IPv6)")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("Resurse online recomandate")] }),
      
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Mininet Walkthrough: http://mininet.org/walkthrough/")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Python ipaddress module: https://docs.python.org/3/library/ipaddress.html")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("IANA IPv4 Special-Purpose Registry: https://www.iana.org/assignments/iana-ipv4-special-registry")] }),
      
      new Paragraph({ spacing: { before: 720 } }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "— Sfârșit document —", size: 20, color: "7B7D7D", italics: true })]
      }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Revolvix&Hypotheticalandrei", size: 16, color: "BDC3C7" })]
      })
    ]
  }]
});

// Save the document
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/claude/starterkit_s5/docs/Curs5_Seminar5_Laborator5.docx", buffer);
  console.log("✓ Document saved: Curs5_Seminar5_Laborator5.docx");
});
