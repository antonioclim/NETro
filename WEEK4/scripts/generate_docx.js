#!/usr/bin/env node
/**
 * Generator document DOCX pentru Săptămâna 4
 * Rețele de Calculatoare - ASE-CSIE
 * Protocoale Text și Binare Custom peste TCP și UDP
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, 
        BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
        ExternalHyperlink } = require('docx');
const fs = require('fs');

// Configurare borduri tabel
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
const headerShading = { fill: "E8F4FD", type: ShadingType.CLEAR };

// Helper pentru paragraf simplu
const p = (text, options = {}) => new Paragraph({
    spacing: { after: 120 },
    ...options,
    children: [new TextRun({ text, size: 24, font: "Arial" })]
});

// Helper pentru paragraf bold
const pb = (text, options = {}) => new Paragraph({
    spacing: { after: 120 },
    ...options,
    children: [new TextRun({ text, size: 24, font: "Arial", bold: true })]
});

// Helper pentru paragraf cu text mixt
const pMix = (parts, options = {}) => new Paragraph({
    spacing: { after: 120 },
    ...options,
    children: parts.map(part => {
        if (typeof part === 'string') {
            return new TextRun({ text: part, size: 24, font: "Arial" });
        }
        return new TextRun({ size: 24, font: "Arial", ...part });
    })
});

// Helper pentru cod inline
const code = (text) => new TextRun({ 
    text, 
    size: 22, 
    font: "Consolas",
    shading: { fill: "F0F0F0", type: ShadingType.CLEAR }
});

// Creare document
const doc = new Document({
    styles: {
        default: { 
            document: { 
                run: { font: "Arial", size: 24 } 
            } 
        },
        paragraphStyles: [
            { 
                id: "Title", name: "Title", basedOn: "Normal",
                run: { size: 56, bold: true, color: "1a365d", font: "Arial" },
                paragraph: { spacing: { before: 240, after: 240 }, alignment: AlignmentType.CENTER }
            },
            { 
                id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 36, bold: true, color: "1a365d", font: "Arial" },
                paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 }
            },
            { 
                id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 30, bold: true, color: "2c5282", font: "Arial" },
                paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 }
            },
            { 
                id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 26, bold: true, color: "3182ce", font: "Arial" },
                paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
            },
            {
                id: "InstructorNote", name: "Instructor Note", basedOn: "Normal",
                run: { size: 22, italics: true, color: "666666", font: "Arial" },
                paragraph: { 
                    spacing: { before: 100, after: 100 },
                    indent: { left: 720 },
                    shading: { fill: "FFF8E1", type: ShadingType.CLEAR }
                }
            }
        ]
    },
    numbering: {
        config: [
            {
                reference: "bullet-list",
                levels: [{
                    level: 0,
                    format: LevelFormat.BULLET,
                    text: "•",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            },
            {
                reference: "numbered-list-1",
                levels: [{
                    level: 0,
                    format: LevelFormat.DECIMAL,
                    text: "%1.",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            },
            {
                reference: "numbered-list-2",
                levels: [{
                    level: 0,
                    format: LevelFormat.DECIMAL,
                    text: "%1.",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            },
            {
                reference: "numbered-list-3",
                levels: [{
                    level: 0,
                    format: LevelFormat.DECIMAL,
                    text: "%1.",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            },
            {
                reference: "numbered-list-ex",
                levels: [{
                    level: 0,
                    format: LevelFormat.DECIMAL,
                    text: "%1.",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            }
        ]
    },
    sections: [{
        properties: {
            page: {
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
            }
        },
        headers: {
            default: new Header({
                children: [new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    children: [
                        new TextRun({ text: "Rețele de Calculatoare | Săptămâna 4", size: 20, font: "Arial", color: "666666" })
                    ]
                })]
            })
        },
        footers: {
            default: new Footer({
                children: [new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({ text: "Pagina ", size: 20, font: "Arial" }),
                        new TextRun({ children: [PageNumber.CURRENT], size: 20, font: "Arial" }),
                        new TextRun({ text: " din ", size: 20, font: "Arial" }),
                        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 20, font: "Arial" }),
                        new TextRun({ text: " | Revolvix&Hypotheticalandrei", size: 18, font: "Arial", color: "999999" })
                    ]
                })]
            })
        },
        children: [
            // TITLU
            new Paragraph({
                heading: HeadingLevel.TITLE,
                children: [new TextRun({ text: "Săptămâna 4", size: 56, bold: true, font: "Arial", color: "1a365d" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 480 },
                children: [new TextRun({ 
                    text: "Protocoale Text și Binare Custom peste TCP și UDP", 
                    size: 36, font: "Arial", color: "2c5282" 
                })]
            }),
            
            // Info disciplină
            new Table({
                columnWidths: [4680, 4680],
                rows: [
                    new TableRow({
                        children: [
                            new TableCell({
                                borders: cellBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pMix([{ text: "Disciplină: ", bold: true }, "Rețele de Calculatoare"])]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pMix([{ text: "Program: ", bold: true }, "Informatică Economică"])]
                            })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({
                                borders: cellBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pMix([{ text: "An: ", bold: true }, "3, Semestrul 2"])]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pMix([{ text: "Durată: ", bold: true }, "2h curs + 2h seminar"])]
                            })
                        ]
                    })
                ]
            }),
            
            // ========== SECȚIUNEA 1 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "1. Scopul săptămânii", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "1.1 Ce vom învăța", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Această săptămână marchează tranziția de la utilizarea protocoalelor standard (HTTP, FTP) la proiectarea și implementarea protocoalelor proprii. Studenții vor dobândi competențele necesare pentru a specifica, implementa și testa protocoale de comunicare adaptate nevoilor specifice ale aplicațiilor."),
            
            pb("Obiective de învățare:"),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Proiectarea protocoalelor text cu format human-readable", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Proiectarea protocoalelor binare cu header fix și payload variabil", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Rezolvarea problemei de framing în TCP streams", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Serializare și deserializare binară cu struct.pack/unpack", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Validarea integrității datelor cu CRC32", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Implementare pattern fire-and-forget pentru UDP", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "1.2 De ce contează", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("În practica profesională, programatorii se confruntă frecvent cu situații în care protocoalele standard nu sunt optimale. Aplicațiile de gaming, IoT, streaming și trading financiar necesită protocoale custom pentru a minimiza latența și overhead-ul. Înțelegerea principiilor de proiectare a protocoalelor permite:"),
            
            new Paragraph({
                numbering: { reference: "numbered-list-1", level: 0 },
                children: [new TextRun({ text: "Optimizarea performanței: reducerea overhead-ului de la sute de bytes (HTTP) la zeci de bytes", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-1", level: 0 },
                children: [new TextRun({ text: "Control granular: specificarea exactă a comportamentului în cazuri de eroare", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-1", level: 0 },
                children: [new TextRun({ text: "Debugging avansat: capacitatea de a analiza și depana traficul la nivel de bytes", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-1", level: 0 },
                children: [new TextRun({ text: "Interoperabilitate: comunicarea cu sisteme embedded și legacy", size: 24, font: "Arial" })]
            }),
            
            // Notă instructor
            new Paragraph({
                style: "InstructorNote",
                spacing: { before: 200, after: 200 },
                shading: { fill: "FFF8E1", type: ShadingType.CLEAR },
                children: [new TextRun({ 
                    text: "📋 Notă instructor: Această săptămână este fundamentală pentru proiectul de echipă. Asigurați-vă că studenții înțeleg că vor trebui să implementeze un protocol custom pentru aplicația lor. Alocați timp pentru întrebări despre cerințele proiectului.", 
                    size: 22, italics: true, font: "Arial", color: "666666" 
                })]
            }),
            
            // ========== SECȚIUNEA 2 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "2. Prerechizite și recapitulare", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "2.1 Cunoștințe necesare din S1-S3", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Table({
                columnWidths: [3120, 3120, 3120],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({
                                borders: cellBorders,
                                shading: headerShading,
                                width: { size: 3120, type: WidthType.DXA },
                                children: [pb("Săptămâna", { alignment: AlignmentType.CENTER })]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                shading: headerShading,
                                width: { size: 3120, type: WidthType.DXA },
                                children: [pb("Concept", { alignment: AlignmentType.CENTER })]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                shading: headerShading,
                                width: { size: 3120, type: WidthType.DXA },
                                children: [pb("Relevanță pentru S4", { alignment: AlignmentType.CENTER })]
                            })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("S1")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Wireshark, tshark, netcat")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Analiza traficului custom")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("S2")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Sockets TCP/UDP de bază")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Fundament pentru protocoale")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("S3")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Server concurent, threading")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Handler clienți multipli")] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 300 },
                children: [new TextRun({ text: "2.2 Recapitulare TCP vs UDP", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Table({
                columnWidths: [4680, 4680],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({
                                borders: cellBorders,
                                shading: headerShading,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pb("TCP (Transmission Control Protocol)", { alignment: AlignmentType.CENTER })]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                shading: headerShading,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [pb("UDP (User Datagram Protocol)", { alignment: AlignmentType.CENTER })]
                            })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Connection-oriented (necesită connect())")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Connectionless (sendto() direct)")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Reliable: ACK, retransmisie automată")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Best-effort: fără garanții de livrare")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Ordered delivery garantată")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Fără garanție de ordine")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Stream-based (bytes continui)")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [p("Message-based (datagrame discrete)")] })
                        ]
                    })
                ]
            }),
            
            // ========== SECȚIUNEA 3 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "3. Curs: Protocoale Custom", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "3.1 Motivația protocoalelor custom", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Protocoalele standard precum HTTP, FTP sau SMTP sunt proiectate pentru versatilitate și interoperabilitate largă. Această generalitate vine cu un cost: overhead semnificativ pentru cazuri simple. Un request HTTP minimal pentru a obține o valoare poate depăși 500 bytes, în timp ce un protocol binar custom poate realiza același lucru în 14-20 bytes."),
            
            pb("Cazuri de utilizare pentru protocoale custom:"),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Gaming: latență minimă, update-uri de stare frecvente", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "IoT/Senzori: dispozitive cu resurse limitate, bandă îngustă", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Trading financiar: microsecunde contează", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Sisteme embedded: memorie și procesor limitate", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "3.2 Protocoale TEXT", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            p("Protocoalele text folosesc caractere ASCII/UTF-8 human-readable. Avantajul principal este debugging-ul facil - traficul poate fi inspectat direct cu netcat sau telnet."),
            
            pb("Format protocol TEXT pentru S4:"),
            p("Mesajele urmează formatul: \"<LUNGIME> <PAYLOAD>\\n\" unde LUNGIME este un număr zecimal reprezentând lungimea payload-ului în bytes, urmat de un spațiu separator și payload-ul propriu-zis, terminat cu newline."),
            
            pMix([{ text: "Exemplu: ", bold: true }, "Clientul trimite \"5 Hello\\n\" - serverul primește și parsează payload-ul \"Hello\"."]),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Problema Framing-ului în TCP", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("TCP este un protocol stream-based, ceea ce înseamnă că datele trimise în apeluri send() separate pot fi primite concatenate într-un singur recv(), sau fragmentate în multiple recv()-uri. Această caracteristică impune necesitatea unui mecanism de delimitare a mesajelor (framing)."),
            
            pb("Soluții de framing:"),
            new Paragraph({
                numbering: { reference: "numbered-list-2", level: 0 },
                children: [new TextRun({ text: "Delimitator fix (newline, null byte) - simplu dar payload-ul nu poate conține delimitatorul", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-2", level: 0 },
                children: [new TextRun({ text: "Lungime prefixată - payload-ul e precedat de lungimea sa", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-2", level: 0 },
                children: [new TextRun({ text: "Header fix - structură cunoscută la început, include lungimea", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "3.3 Protocoale BINARE", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Protocoalele binare encodează datele în format binar compact. Principalele avantaje sunt eficiența (overhead minim) și performanța (parsing rapid). Dezavantajul este că debugging-ul necesită instrumente specializate (Wireshark, hex dump)."),
            
            pb("Structura header-ului BINAR pentru S4 (14 bytes):"),
            
            new Table({
                columnWidths: [1500, 1200, 2000, 4660],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 1500, type: WidthType.DXA }, children: [pb("Offset", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 1200, type: WidthType.DXA }, children: [pb("Bytes", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 2000, type: WidthType.DXA }, children: [pb("Câmp", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 4660, type: WidthType.DXA }, children: [pb("Descriere", { alignment: AlignmentType.CENTER })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("0")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("2")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("MAGIC")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("\"NP\" (0x4E50) - identificator protocol")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("2")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("1")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("VERSION")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("Versiune protocol (0x01)")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("3")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("1")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("TYPE")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("Tip mesaj (0=req, 1=resp, 2=error)")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("4")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("4")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("PAYLOAD_LEN")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("Lungime payload (big-endian, uint32)")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("8")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("2")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("SEQUENCE")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("Număr secvență (big-endian, uint16)")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 1500, type: WidthType.DXA }, children: [p("10")] }),
                            new TableCell({ borders: cellBorders, width: { size: 1200, type: WidthType.DXA }, children: [p("4")] }),
                            new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA }, children: [p("CRC32")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4660, type: WidthType.DXA }, children: [p("Checksum payload (big-endian, uint32)")] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                spacing: { before: 300 },
                children: [new TextRun({ text: "Serializare cu struct în Python", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Modulul struct din Python permite conversia între valori Python și reprezentări binare. Formatul '>2sBBIHI' specifică: big-endian (>), 2 bytes string (2s), două unsigned char (BB), unsigned int (I), unsigned short (H), unsigned int (I)."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "3.4 Protocol UDP pentru senzori", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("UDP este ideal pentru aplicații care necesită latență minimă și tolerează pierderi ocazionale. Un senzor IoT care trimite citiri la fiecare 2 secunde poate tolera pierderea unei citiri - următoarea oricum vine curând."),
            
            pb("Format datagramă senzor (23 bytes fix):"),
            p("Versiune (1B) + SensorID (4B) + Temperatură float (4B) + Locație ASCII padded (10B) + CRC32 (4B)"),
            
            // Note instructor
            new Paragraph({
                style: "InstructorNote",
                spacing: { before: 200, after: 200 },
                shading: { fill: "FFF8E1", type: ShadingType.CLEAR },
                children: [new TextRun({ 
                    text: "📋 Notă instructor: La acest punct, demonstrați live diferența dintre TEXT și BINAR capturând trafic cu tshark. Arătați payload-ul TEXT direct în ASCII vs hex dump pentru BINAR. Timing estimat: 5-7 minute.", 
                    size: 22, italics: true, font: "Arial", color: "666666" 
                })]
            }),
            
            // ========== SECȚIUNEA 4 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "4. Seminar: Implementare ghidată", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "4.1 Pregătire mediu de lucru", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Înainte de a începe implementarea, verificați că aveți toate instrumentele necesare instalate și funcționale."),
            
            pb("Comenzi de verificare:"),
            p("python3 --version (necesită 3.8+)"),
            p("pip3 --version"),
            p("tshark --version"),
            p("nc -h (netcat)"),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "4.2 Implementare Protocol TEXT - pas cu pas", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 1: Funcția recv_until()", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Această funcție citește bytes din socket până întâlnește delimitatorul specificat. Este esențială pentru protocoale text care folosesc newline sau alt caracter ca terminator de mesaj."),
            
            pb("Pseudocod:"),
            p("1. Inițializează buffer gol"),
            p("2. Repetă: citește 1 byte, adaugă la buffer"),
            p("3. Dacă delimitatorul e în buffer, returnează buffer"),
            p("4. Dacă conexiunea s-a închis (recv returnează empty), ridică excepție"),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 2: Funcția parse_message()", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Extrage lungimea declarată și payload-ul din formatul '<LEN> <PAYLOAD>'. Validează că lungimea declarată corespunde cu lungimea reală a payload-ului."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 3: Handler client", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Funcția handle_client primește conexiunea acceptată și procesează mesaje în buclă până la deconectare. Fiecare mesaj primit e parsăt, procesat (ecou în exemplul nostru) și răspunsul e trimis înapoi."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "4.3 Implementare Protocol BINAR - pas cu pas", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 1: Funcția recv_exact()", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Spre deosebire de recv_until(), această funcție citește exact N bytes, acumulând în buffer până ajunge la lungimea cerută. Este necesară deoarece recv(n) poate returna mai puțin de n bytes."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 2: Pack și Unpack header", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("Utilizați struct.pack pentru a crea header-ul și struct.unpack pentru a-l citi. Formatul '>2sBBIHI' corespunde structurii definite (14 bytes total)."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({ text: "Pasul 3: Calcul și validare CRC32", size: 26, bold: true, font: "Arial", color: "3182ce" })]
            }),
            p("CRC32 se calculează peste payload cu zlib.crc32(data) & 0xFFFFFFFF. Masca & 0xFFFFFFFF asigură rezultat unsigned pe 32 biți. La recepție, comparați CRC-ul din header cu cel calculat local."),
            
            // Note instructor
            new Paragraph({
                style: "InstructorNote",
                spacing: { before: 200, after: 200 },
                shading: { fill: "FFF8E1", type: ShadingType.CLEAR },
                children: [new TextRun({ 
                    text: "📋 Notă instructor: Lăsați studenții să implementeze singuri recv_exact() (5 min), apoi discutați soluțiile. Greșeli comune: nu verifică dacă recv() returnează empty bytes (conexiune închisă).", 
                    size: 22, italics: true, font: "Arial", color: "666666" 
                })]
            }),
            
            // ========== SECȚIUNEA 5 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "5. Laborator: Experimente practice", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "5.1 Experiment 1: Protocol TEXT funcțional", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Obiectiv: Rularea și testarea serverului și clientului TEXT."),
            
            pb("Pași:"),
            new Paragraph({
                numbering: { reference: "numbered-list-3", level: 0 },
                children: [new TextRun({ text: "Deschideți Terminal 1, navigați la /python/apps/", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-3", level: 0 },
                children: [new TextRun({ text: "Porniți serverul: python3 text_proto_server.py", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-3", level: 0 },
                children: [new TextRun({ text: "Deschideți Terminal 2, testați cu netcat: echo '5 Hello' | nc localhost 3333", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-3", level: 0 },
                children: [new TextRun({ text: "Rulați clientul Python: python3 text_proto_client.py", size: 24, font: "Arial" })]
            }),
            
            pb("Rezultat așteptat:"),
            p("Serverul afișează mesajele primite și trimite ecou înapoi. Clientul primește răspunsurile și le afișează."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "5.2 Experiment 2: Captură și analiză trafic", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Obiectiv: Capturarea și analiza traficului TEXT și BINAR cu tshark."),
            
            pb("Comenzi pentru captură TEXT:"),
            p("sudo tshark -i lo -f 'tcp port 3333' -Y 'tcp.payload' -T fields -e frame.number -e tcp.payload"),
            
            pb("Comenzi pentru captură BINAR:"),
            p("sudo tshark -i lo -f 'tcp port 4444' -Y 'tcp.payload' -x"),
            
            pb("Întrebări de analiză:"),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Ce observați în payload-ul TEXT vs BINAR?", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Puteți identifica header-ul de 14 bytes în traficul BINAR?", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Care este overhead-ul pentru un mesaj 'Hello' în fiecare protocol?", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "5.3 Experiment 3: Simulare senzori UDP în Mininet", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Obiectiv: Testarea protocolului UDP sensor într-o topologie izolată."),
            
            p("Utilizați scenariul Mininet din /mininet/scenario_udp_demo.py care creează o topologie cu 2 senzori și un colector, incluzând simulare de pierderi pe una din legături."),
            
            // ========== SECȚIUNEA 6 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "6. Greșeli frecvente și debugging", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Table({
                columnWidths: [3000, 3000, 3360],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3000, type: WidthType.DXA }, children: [pb("Simptom", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3000, type: WidthType.DXA }, children: [pb("Cauză probabilă", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3360, type: WidthType.DXA }, children: [pb("Diagnostic", { alignment: AlignmentType.CENTER })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("recv() blochează indefinit")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Nu s-a trimis suficient")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3360, type: WidthType.DXA }, children: [p("Verifică dacă \\n e trimis")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Date trunchiare")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("recv() < bytes așteptați")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3360, type: WidthType.DXA }, children: [p("Folosește recv_exact()")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("CRC mismatch constant")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Endianness greșit")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3360, type: WidthType.DXA }, children: [p("Verifică > vs < în format")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Magic invalid")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Offset greșit în unpack")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3360, type: WidthType.DXA }, children: [p("Verifică HEADER_SIZE")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Conexiune refuzată")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3000, type: WidthType.DXA }, children: [p("Server nu ascultă")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3360, type: WidthType.DXA }, children: [p("netstat -tlnp | grep PORT")] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 300 },
                children: [new TextRun({ text: "6.1 Comenzi utile de debugging", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Verificare port activ:"),
            p("netstat -tlnp | grep 3333"),
            
            pb("Test conexiune rapidă:"),
            p("nc -v localhost 3333"),
            
            pb("Captură raw pe interfață:"),
            p("sudo tcpdump -i lo port 3333 -XX"),
            
            pb("Verificare procese Python:"),
            p("ps aux | grep python"),
            
            // ========== SECȚIUNEA 7 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "7. Exerciții de consolidare", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercițiu 1: Protocol TEXT cu comenzi (Înțelegere)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Extindeți protocolul TEXT pentru a suporta comenzi multiple: ECHO, UPPER, LOWER, REVERSE, COUNT. Formatul devine \"<CMD> <LEN> <PAYLOAD>\\n\". Serverul trebuie să proceseze comanda și să returneze rezultatul corespunzător."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercițiu 2: Analiza overhead (Aplicare)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Capturați 10 mesaje TEXT și 10 BINAR. Calculați overhead-ul total (bytes protocol / bytes payload) pentru fiecare. Răspundeți: care protocol e mai eficient pentru payload de 5 bytes? Dar pentru 500 bytes?"),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercițiu 3: Protocol BINAR cu tipuri (Aplicare)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Extindeți header-ul BINAR cu un câmp CONTENT_TYPE: 0=text UTF-8, 1=JSON, 2=bytes raw. Serverul trebuie să proceseze diferit fiecare tip (pentru JSON: deserializare și extragere câmp specific)."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercițiu 4: Agregator UDP (Analiză)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Creați un agregator care primește date de la multipli senzori și: (a) calculează media temperaturii per locație, (b) detectează senzori care nu au trimis în ultimele 30 secunde, (c) generează raport JSON periodic."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercițiu 5: Testare în Mininet (Sinteză)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Implementați o topologie Mininet cu 3 hosturi și testați protocolul BINAR. Adăugați delay de 50ms pe o legătură cu 'tc netem' și măsurați impactul asupra throughput-ului."),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "Exercițiu 6 - Challenge: Protocol hibrid (Creație)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Proiectați și implementați un protocol hibrid care: (1) folosește handshake TEXT pentru negociere capabilități, (2) trece la mod BINAR pentru transfer date, (3) suportă compresie opțională zlib, (4) include timestamp în fiecare mesaj. Livrați specificație documentată, implementare server+client, și captură tshark demonstrativă."),
            
            // ========== SECȚIUNEA 8 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "8. Mini-reflecție", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "8.1 Ce am învățat", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Concepte fundamentale:"),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Diferența fundamentală între protocoale text (human-readable) și binare (compact, eficient)", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Problema framing-ului în TCP și soluții: delimitatori, lungime prefixată, header fix", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Tehnici de citire: recv_until() pentru text, recv_exact() pentru binar", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Serializare binară cu struct.pack/unpack și convenții endianness", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Validarea integrității cu CRC32 - detectare erori, nu securitate", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Caracteristicile UDP pentru aplicații fire-and-forget", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "8.2 Unde se folosește în practică", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Table({
                columnWidths: [3120, 3120, 3120],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3120, type: WidthType.DXA }, children: [pb("Domeniu", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3120, type: WidthType.DXA }, children: [pb("Exemplu protocol", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 3120, type: WidthType.DXA }, children: [pb("Caracteristici", { alignment: AlignmentType.CENTER })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Cache/DB")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Redis RESP, Memcached")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Text simplu, high throughput")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Gaming")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Protocol custom UDP")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Latență minimă, toleranță pierderi")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("IoT")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("MQTT, CoAP")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Overhead minim, dispozitive limitate")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("RPC")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("gRPC (Protocol Buffers)")] }),
                            new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, children: [p("Binar eficient, schema-based")] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 300 },
                children: [new TextRun({ text: "8.3 Legătura cu rolul de programator", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Competențele dobândite în această săptămână sunt direct aplicabile în roluri precum: Backend Developer (design API-uri eficiente), Systems Programmer (comunicare inter-proces), Embedded Developer (protocoale pentru microcontrolere), Game Developer (networking multiplayer), IoT Engineer (protocoale senzori)."),
            
            // ========== SECȚIUNEA 9 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "9. Contribuția la proiectul de echipă", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "9.1 Artefact S4: Protocol custom pentru aplicație", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            pb("Cerințe minime:"),
            new Paragraph({
                numbering: { reference: "numbered-list-ex", level: 0 },
                children: [new TextRun({ text: "Specificație documentată: format header, tipuri mesaje, diagrame", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-ex", level: 0 },
                children: [new TextRun({ text: "Implementare server și client funcționale", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-ex", level: 0 },
                children: [new TextRun({ text: "Minim 3 tipuri de mesaje/comenzi diferite", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-ex", level: 0 },
                children: [new TextRun({ text: "Validare integritate (CRC sau alt mecanism)", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list-ex", level: 0 },
                children: [new TextRun({ text: "Captură tshark demonstrativă cu interpretare", size: 24, font: "Arial" })]
            }),
            
            pb("Criterii bonus:"),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Protocol hibrid (negociere TEXT → transfer BINAR)", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Compresie payload opțională", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Suport pentru multiple versiuni protocol", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Teste automate pentru protocol", size: 24, font: "Arial" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "9.2 Integrare în arhitectura proiectului", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            p("Protocolul dezvoltat trebuie să se integreze în arhitectura generală a aplicației de echipă. Documentați în README cum se poziționează protocolul: ce componente îl folosesc, ce date transportă, și de ce ați ales această abordare (TEXT vs BINAR)."),
            
            // ========== SECȚIUNEA 10 ==========
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: "10. Bibliografie și resurse", size: 36, bold: true, font: "Arial", color: "1a365d" })]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: "10.1 Bibliografie academică cu DOI", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Table({
                columnWidths: [5000, 4360],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 5000, type: WidthType.DXA }, children: [pb("Referință", { alignment: AlignmentType.CENTER })] }),
                            new TableCell({ borders: cellBorders, shading: headerShading, width: { size: 4360, type: WidthType.DXA }, children: [pb("DOI / Link", { alignment: AlignmentType.CENTER })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 5000, type: WidthType.DXA }, children: [p("Kurose, J. & Ross, K. (2021). Computer Networking: A Top-Down Approach (8th ed.). Pearson.")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4360, type: WidthType.DXA }, children: [p("ISBN: 978-0135928615")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 5000, type: WidthType.DXA }, children: [p("Stevens, W.R. (1993). TCP/IP Illustrated, Vol. 1: The Protocols. Addison-Wesley.")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4360, type: WidthType.DXA }, children: [p("ISBN: 978-0201633467")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 5000, type: WidthType.DXA }, children: [p("Rhodes, B. & Goerzen, J. (2014). Foundations of Python Network Programming (3rd ed.). Apress.")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4360, type: WidthType.DXA }, children: [p("DOI: 10.1007/978-1-4302-5855-1")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 5000, type: WidthType.DXA }, children: [p("Postel, J. (1981). Transmission Control Protocol. RFC 793.")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4360, type: WidthType.DXA }, children: [p("DOI: 10.17487/RFC0793")] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, width: { size: 5000, type: WidthType.DXA }, children: [p("Postel, J. (1980). User Datagram Protocol. RFC 768.")] }),
                            new TableCell({ borders: cellBorders, width: { size: 4360, type: WidthType.DXA }, children: [p("DOI: 10.17487/RFC0768")] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 300 },
                children: [new TextRun({ text: "10.2 Standarde și specificații (fără DOI)", size: 30, bold: true, font: "Arial", color: "2c5282" })]
            }),
            
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Python struct module documentation: https://docs.python.org/3/library/struct.html", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Python zlib module documentation: https://docs.python.org/3/library/zlib.html", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Wireshark User's Guide: https://www.wireshark.org/docs/wsug_html/", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Mininet Documentation: http://mininet.org/walkthrough/", size: 24, font: "Arial" })]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: "Redis Protocol Specification (RESP): https://redis.io/docs/reference/protocol-spec/", size: 24, font: "Arial" })]
            }),
            
            // Footer final
            new Paragraph({
                spacing: { before: 600 },
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ 
                    text: "─── Revolvix&Hypotheticalandrei ───", 
                    size: 20, font: "Arial", color: "999999", italics: true 
                })]
            })
        ]
    }]
});

// Generare și salvare
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync('/home/claude/output/starterkit_s4/Curs4_Seminar4_Laborator4.docx', buffer);
    console.log('✓ Document DOCX generat: Curs4_Seminar4_Laborator4.docx');
}).catch(err => {
    console.error('Eroare la generare DOCX:', err);
    process.exit(1);
});
