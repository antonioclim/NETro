# 1. Introducere în Securitatea Rețelelor și IoT

## 1.1 Contextul Actual al Securității Cibernetice

Securitatea rețelelor de calculatoare reprezintă unul dintre domeniile cu cea mai rapidă evoluție din informatică, determinată de creșterea exponențială a dispozitivelor conectate și de sofisticarea atacurilor cibernetice. În contextul Industriei 4.0 și al digitalizării accelerate, înțelegerea mecanismelor de atac și apărare devine esențială pentru orice specialist IT.

### Triada CIA (Confidentiality, Integrity, Availability)

Fundamentul securității informaționale se bazează pe trei piloni interdependenți:

**Confidențialitatea** asigură că informațiile sunt accesibile exclusiv entităților autorizate. În contextul IoT, aceasta implică:
- Criptarea datelor în tranzit (TLS/DTLS)
- Criptarea datelor în repaus (AES-256)
- Mecanisme solide de autentificare
- Controlul granular al accesului

**Integritatea** garantează că datele nu au fost modificate neautorizat între sursă și destinație. Mecanismele includ:
- Hash-uri criptografice (SHA-256, SHA-3)
- Semnături digitale (RSA, ECDSA)
- Message Authentication Codes (HMAC)
- Blockchain pentru audit trail imutabil

**Disponibilitatea** asigură accesul neîntrerupt la servicii pentru utilizatorii legitimi:
- Redundanță la nivel de infrastructură
- Protecție împotriva atacurilor DoS/DDoS
- Backup și disaster recovery
- SLA (Service Level Agreements) cu metrici clare

### Defense in Depth

Strategia „Defense in Depth" (apărare în adâncime) presupune implementarea mai multor straturi de securitate, astfel încât compromiterea unui strat să nu expună întregul sistem:

```
┌─────────────────────────────────────────────────┐
│              Politici și Proceduri              │  Layer 7
├─────────────────────────────────────────────────┤
│         Securitate la Nivel Aplicație          │  WAF, Input Validation
├─────────────────────────────────────────────────┤
│              Securitate Host                    │  AV, HIDS, Hardening
├─────────────────────────────────────────────────┤
│            Securitate Rețea Internă            │  IDS/IPS, Segmentare
├─────────────────────────────────────────────────┤
│              Securitate Perimetru              │  Firewall, DMZ
├─────────────────────────────────────────────────┤
│            Securitate Fizică                    │  Acces controlat
└─────────────────────────────────────────────────┘
```

## 1.2 Evoluția Amenințărilor Cibernetice

### Taxonomia Atacatorilor

**Script Kiddies** - Atacatori cu competențe tehnice limitate care utilizează instrumente și exploit-uri dezvoltate de alții. Deși par mai puțin periculoși, volumul mare de atacuri automatizate pe care le generează reprezintă o amenințare constantă.

**Hacktivists** - Motivați ideologic, vizează organizații pentru a face declarații politice sau sociale. Atacurile DDoS și defacement-ul sunt tactici comune.

**Cybercriminals** - Motivați financiar, utilizează ransomware, phishing, și fraude pentru profit. Operează adesea ca organizații structurate cu lanțuri de aprovizionare proprii (Ransomware-as-a-Service).

**Nation-State Actors (APT)** - Grupări sponsorizate de state, cu resurse nelimitate și obiective de spionaj, sabotaj sau pregătire pentru conflicte cibernetice. Caracterizate prin:
- Persistență pe termen lung (luni/ani)
- Tehnici avansate de evaziune
- Zero-day exploits
- Supply chain attacks

### Modelul Cyber Kill Chain

Dezvoltat de Lockheed Martin, acest model descrie fazele unui atac cibernetic:

1. **Reconnaissance** - Culegerea de informații despre țintă
2. **Weaponization** - Crearea payload-ului malițios
3. **Delivery** - Livrarea către victimă (email, web, USB)
4. **Exploitation** - Exploatarea unei vulnerabilități
5. **Installation** - Instalarea malware-ului persistent
6. **Command & Control (C2)** - Stabilirea comunicării cu atacatorul
7. **Actions on Objectives** - Îndeplinirea obiectivelor (exfiltrare, sabotaj)

Apărătorii pot întrerupe atacul în orice fază. Cu cât detectarea este mai timpurie, cu atât impactul este mai redus.

## 1.3 Specificul Securității IoT

### Caracteristicile Ecosistemului IoT

Internet of Things introduce provocări unice de securitate datorită:

**Constrângerilor de resurse** - Dispozitivele IoT au frecvent:
- Procesoare cu putere de calcul limitată (8/16/32-bit MCU)
- Memorie RAM redusă (KB, nu MB)
- Stocare minimă (flash intern)
- Baterie/energie solară ca sursă de alimentare

**Heterogenității** - Ecosistemul include:
- Senzori simpli (temperatură, umiditate, mișcare)
- Actuatoare (valve, motoare, relee)
- Gateway-uri și concentratoare
- Platforme cloud pentru agregare și analiză
- Protocoale diverse (MQTT, CoAP, Zigbee, LoRa, BLE)

**Ciclului de viață extins** - Dispozitivele IoT industriale pot funcționa 10-15 ani, timp în care:
- Suportul producătorului poate înceta
- Vulnerabilități noi sunt descoperite
- Actualizările firmware devin imposibile sau riscante

### Suprafața de Atac IoT

```
┌──────────────────────────────────────────────────────────────┐
│                    ATTACK SURFACE IoT                        │
├────────────────┬─────────────────┬───────────────────────────┤
│   DISPOZITIV   │    COMUNICAȚIE   │         CLOUD            │
├────────────────┼─────────────────┼───────────────────────────┤
│ Firmware       │ Protocol Radio  │ API Endpoints             │
│ Debug Ports    │ Gateway         │ Storage                   │
│ Physical       │ TLS/DTLS Config │ Authentication            │
│ Boot Process   │ Key Exchange    │ Multi-tenancy             │
│ Memory         │ Replay Attacks  │ Data Leakage              │
└────────────────┴─────────────────┴───────────────────────────┘
```

## 1.4 Cadrul Legal și Standarde

### Reglementări Relevante

**GDPR (General Data Protection Regulation)** - Regulamentul european privind protecția datelor personale se aplică și dispozitivelor IoT care colectează date despre persoane. Cerințe cheie:
- Privacy by Design și Privacy by Default
- Minimizarea datelor colectate
- Dreptul la ștergere („right to be forgotten")
- Notificarea breșelor de securitate în 72 ore

**NIS2 Directive** - Directiva privind securitatea rețelelor și sistemelor informatice impune:
- Măsuri tehnice și organizaționale proporționale cu riscul
- Raportarea incidentelor către autoritățile competente
- Audit și certificare pentru sectoarele critice

**Cyber Resilience Act (propus)** - Va impune:
- Cerințe de securitate pentru produse cu elemente digitale
- Actualizări de securitate pe întreaga durată de viață
- Marcaj CE condiționat de conformitate

### Standarde Tehnice

**IEC 62443** - Seria de standarde pentru securitatea sistemelor de automatizare industrială (ICS/SCADA):
- Zonare și conducte (zones and conduits)
- Niveluri de securitate (SL 1-4)
- Cerințe pentru componente, sisteme și procese

**OWASP IoT Top 10** - Cele mai critice 10 vulnerabilități IoT:
1. Parole slabe sau hardcodate
2. Servicii de rețea nesecurizate
3. Interfețe ecosistem nesecurizate
4. Lipsa mecanismelor de actualizare
5. Componente nesigure sau depreciate
6. Protecție insuficientă a confidențialității
7. Transfer și stocare nesigură a datelor
8. Lipsa managementului dispozitivelor
9. Setări implicite nesigure
10. Lipsa hardening-ului fizic

## 1.5 Metodologia Practică

### Abordarea Duală: Ofensiv + Defensiv

Acest curs adoptă o abordare duală, recunoscând că:

> „Pentru a te apăra eficient, trebuie să gândești ca un atacator."

**Perspectiva Ofensivă (Red Team):**
- Înțelegerea lanțului de atac
- Utilizarea instrumentelor de pentest
- Identificarea și exploatarea vulnerabilităților
- Documentarea și raportarea găsirilor

**Perspectiva Defensivă (Blue Team):**
- Implementarea controalelor de securitate
- Monitorizarea și detectarea anomaliilor
- Segmentarea și izolarea rețelelor
- Răspunsul la incidente

### Mediul de Laborator

Laboratorul utilizează un mediu containerizat și virtualizat:

```
┌─────────────────────────────────────────────────────────────┐
│                     DOCKER NETWORK                          │
│                    (172.20.0.0/24)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  DVWA    │  │ WebGoat  │  │  vsftpd  │  │ mosquitto│    │
│  │  :80     │  │  :8080   │  │  :21     │  │  :1883   │    │
│  │ vuln/web │  │ vuln/web │  │ vuln/ftp │  │ mqtt/iot │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   MININET SIMULATION                         │
│                    (10.0.0.0/24)                             │
│  ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐   │
│  │sensor1 │────▶│   s1   │◀────│ broker │◀────│attacker│   │
│  │10.0.0.11│    │(switch)│     │10.0.0.100    │10.0.0.50│   │
│  └────────┘     └────────┘     └────────┘     └────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Fluxul de Lucru Recomandat

1. **Setup** - Pregătirea mediului (`make setup`)
2. **Reconnaissance** - Descoperirea infrastructurii
3. **Scanning** - Identificarea serviciilor și versiunilor
4. **Vulnerability Assessment** - Verificarea CVE-urilor
5. **Exploitation** - Demonstrarea impactului (în mediu controlat)
6. **Defense Implementation** - Aplicarea contramăsurilor
7. **Verification** - Validarea eficienței apărării
8. **Documentation** - Raportarea completă

## 1.6 Considerații Etice

### Principii Fundamentale

Activitățile de security testing trebuie să respecte:

**Autorizare explicită** - Niciodată nu testați sisteme fără permisiune scrisă. Mediul de laborator oferit este singura țintă legitimă.

**Proporționalitate** - Utilizați forța minimă necesară pentru a demonstra o vulnerabilitate. Nu distrugeți, nu exfiltrați date reale, nu perturbați servicii de producție.

**Confidențialitate** - Rapoartele de vulnerabilitate trebuie gestionate cu discreție, împărtășite doar cu părțile autorizate.

**Responsible Disclosure** - Când descoperiți vulnerabilități în software public:
1. Raportați producătorului/dezvoltatorului
2. Acordați timp rezonabil pentru remediere (90 zile standard)
3. Publicați doar după patch sau expirarea termenului

### Cadrul Legal Românesc

**Legea 161/2003** (Criminalitatea Informatică) incriminează:
- Accesul neautorizat la sisteme informatice
- Interceptarea ilegală a comunicațiilor
- Alterarea integrității datelor
- Perturbarea funcționării sistemelor

Penalități: amenzi și închisoare de la 1 la 12 ani în funcție de gravitate.

**Excepții legitime:**
- Testare autorizată (penetration testing cu contract)
- Cercetare academică în medii izolate
- Activități de Blue Team în infrastructură proprie

---

## Rezumat

Securitatea rețelelor și IoT reprezintă un domeniu complex care necesită înțelegerea atât a mecanismelor de atac, cât și a strategiilor de apărare. Triada CIA, modelul Defense in Depth și Cyber Kill Chain oferă cadre conceptuale pentru abordarea sistematică a securității. Specificul IoT (resurse limitate, heterogenitate, ciclu de viață extins) amplifică provocările tradiționale. Respectarea cadrului legal și etic este obligatorie pentru orice practician în domeniu.

## Întrebări de Verificare

1. Care sunt cele trei componente ale triadei CIA și cum se aplică în contextul IoT?
2. Explicați diferența dintre Defense in Depth și securitatea perimetrală tradițională.
3. Care sunt principalele categorii de atacatori și ce îi motivează?
4. De ce sunt dispozitivele IoT deosebit de vulnerabile comparativ cu serverele tradiționale?
5. Care sunt implicațiile GDPR pentru un sistem IoT care colectează date de localizare?

## Referințe

- NIST Cybersecurity Framework v2.0 (2024)
- OWASP IoT Top 10 (2024)
- IEC 62443 Series (Industrial Cybersecurity)
- Kurose & Ross - Computer Networking: A Top-Down Approach, 7th Ed.
