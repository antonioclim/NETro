# Diagrame PlantUML - Săptămânile 1-14

72 de diagrame optimizate pentru randare pe serverul HTTP PlantUML.

## Probleme Rezolvate
- Eliminată sintaxa `note as` (cauza randări goale)
- Eliminate note complexe multi-linie
- Folosit `legend` pentru text explicativ
- Sintaxă simplificată pentru compatibilitate API HTTP

## Generare

### Folosind serverul PlantUML (online)
```bash
python3 generate_png_simple.py
```

### Folosind JAR local (recomandat)
```bash
# Descarcă JAR-ul o singură dată
wget https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar

# Generează toate PNG-urile
java -jar plantuml.jar -tpng week*/*.puml
```

### Format A4 pentru tipărire
```bash
pip install Pillow
python3 generate_a4.py --dpi 150 --output-dir ./png_a4
```

## Structură
- week01-14/: 5-6 diagrame per săptămână
- Fiecare diagramă folosește doar sintaxă PlantUML validată
- Culori: paletă Material Design
- Font: Arial (cross-platform)

## Utilizare în Curs

Diagramele sunt referite în materialele de curs și seminar. Pentru a le include în prezentări:

1. Generează PNG-urile cu unul din scripturile de mai sus
2. Copiază fișierele `.png` în slide-uri
3. Pentru print, folosește varianta A4 cu DPI 150+

## Troubleshooting

**JAR nu se descarcă:**
```bash
# Alternativă cu curl
curl -L -o plantuml.jar https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar
```

**Java lipsește:**
```bash
sudo apt install default-jre
```

**Diagrama nu se generează:**
- Verifică sintaxa în editorul online: https://www.plantuml.com/plantuml/uml/
- Asigură-te că fișierul începe cu `@startuml` și se termină cu `@enduml`
