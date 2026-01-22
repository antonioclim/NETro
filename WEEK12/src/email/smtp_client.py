#!/usr/bin/env python3
"""
smtp_client.py - Client SMTP Didactic pentru Săptămâna 12

Acest modul demonstrează:
- Utilizarea bibliotecii smtplib din Python
- Construirea mesajelor email cu modulul email
- Diferența între envelope și message headers
- MIME pentru atașamente

Utilizare:
    python3 smtp_client.py --host 127.0.0.1 --port 1025 \\
        --from sender@test --to recipient@test \\
        --subject "Test" --body "Mesaj de test"

Revolvix&Hypotheticalandrei
"""

import argparse
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional


def create_simple_message(
    sender: str,
    recipients: List[str],
    subject: str,
    body: str
) -> MIMEText:
    """
    Crează un mesaj email simplu (text/plain).
    
    Args:
        sender: Adresa expeditorului
        recipients: Lista de destinatari
        subject: Subiectul mesajului
        body: Corpul mesajului
    
    Returns:
        MIMEText: Obiectul mesaj gata de trimitere
    
    Concepte demonstrate:
    - Antetele mesajului (From, To, Subject, Date)
    - Diferența dintre envelope și message headers
    """
    msg = MIMEText(body, 'plain', 'utf-8')
    
    # Antetele mesajului (Message Headers - RFC 5322)
    # ATENȚIE: Acestea pot diferi de envelope (MAIL FROM, RCPT TO)!
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
    msg['X-Mailer'] = 'S12 SMTP Client (Python smtplib)'
    
    return msg


def create_multipart_message(
    sender: str,
    recipients: List[str],
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    attachments: Optional[List[Path]] = None
) -> MIMEMultipart:
    """
    Crează un mesaj MIME multipart cu HTML și/sau atașamente.
    
    Args:
        sender: Adresa expeditorului
        recipients: Lista de destinatari
        subject: Subiectul
        body_text: Corpul în format text
        body_html: Corpul în format HTML (opțional)
        attachments: Lista de fișiere de atașat (opțional)
    
    Returns:
        MIMEMultipart: Mesajul complet
    
    Concepte demonstrate:
    - multipart/mixed: mesaj cu atașamente
    - multipart/alternative: versiuni text + HTML
    - Content-Type și Content-Transfer-Encoding
    """
    # Tipul de multipart depinde de conținut
    if attachments:
        msg = MIMEMultipart('mixed')
    elif body_html:
        msg = MIMEMultipart('alternative')
    else:
        msg = MIMEMultipart()
    
    # Antete
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
    msg['MIME-Version'] = '1.0'
    msg['X-Mailer'] = 'S12 SMTP Client (Python email.mime)'
    
    # Corp text
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
    
    # Corp HTML (dacă e specificat)
    if body_html:
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))
    
    # Atașamente
    if attachments:
        for filepath in attachments:
            if filepath.exists():
                with open(filepath, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{filepath.name}"'
                    )
                    msg.attach(part)
    
    return msg


def send_email(
    host: str,
    port: int,
    sender: str,
    recipients: List[str],
    subject: str,
    body: str,
    use_tls: bool = False,
    username: Optional[str] = None,
    password: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """
    Trimite un email prin SMTP.
    
    Args:
        host: Hostname-ul serverului SMTP
        port: Portul SMTP
        sender: Adresa expeditorului (envelope MAIL FROM)
        recipients: Lista de destinatari (envelope RCPT TO)
        subject: Subiectul mesajului
        body: Corpul mesajului
        use_tls: Folosește STARTTLS
        username: Username pentru autentificare (opțional)
        password: Parolă pentru autentificare (opțional)
        verbose: Mod verbose pentru debugging
    
    Returns:
        bool: True dacă trimiterea a reușit
    
    Demonstrație:
    - Conexiune SMTP
    - EHLO/HELO
    - MAIL FROM, RCPT TO, DATA
    - QUIT
    """
    # Creare mesaj
    msg = create_simple_message(sender, recipients, subject, body)
    
    try:
        # Conectare la server
        if verbose:
            print(f"[INFO] Conectare la {host}:{port}...")
        
        smtp = smtplib.SMTP(host, port, timeout=10)
        
        # Activare debugging SMTP (afișează conversația)
        if verbose:
            smtp.set_debuglevel(2)
        
        # EHLO
        smtp.ehlo()
        
        # STARTTLS (dacă e cerut și suportat)
        if use_tls:
            if smtp.has_extn('STARTTLS'):
                smtp.starttls()
                smtp.ehlo()  # Re-EHLO după TLS
            else:
                print("[WARN] Server nu suportă STARTTLS")
        
        # Autentificare (dacă e cerută)
        if username and password:
            smtp.login(username, password)
        
        # Trimitere mesaj
        # NOTĂ: sendmail() folosește:
        #   - sender -> MAIL FROM (envelope)
        #   - recipients -> RCPT TO (envelope)
        #   - msg.as_string() -> DATA (mesajul propriu-zis)
        smtp.sendmail(sender, recipients, msg.as_string())
        
        print(f"[OK] Email trimis către {', '.join(recipients)}")
        
        # Închidere conexiune
        smtp.quit()
        
        return True
        
    except smtplib.SMTPConnectError as e:
        print(f"[ERR] Nu s-a putut conecta la server: {e}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERR] Autentificare eșuată: {e}")
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[ERR] Destinatari refuzați: {e}")
    except smtplib.SMTPDataError as e:
        print(f"[ERR] Eroare la trimiterea datelor: {e}")
    except smtplib.SMTPException as e:
        print(f"[ERR] Eroare SMTP: {e}")
    except Exception as e:
        print(f"[ERR] Eroare: {e}")
    
    return False


def interactive_mode(host: str, port: int):
    """
    Mod interactiv pentru trimiterea manuală de comenzi SMTP.
    
    Util pentru înțelegerea protocolului la nivel scăzut.
    """
    import socket
    
    print(f"[INFO] Mod interactiv - conectare la {host}:{port}")
    print("[INFO] Comenzi disponibile: HELO, EHLO, MAIL FROM, RCPT TO, DATA, QUIT")
    print("[INFO] Tastați 'exit' pentru a ieși")
    print()
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.settimeout(5)
        
        # Citire banner
        banner = sock.recv(1024).decode()
        print(f"S: {banner.strip()}")
        
        while True:
            cmd = input("C: ").strip()
            if cmd.lower() == 'exit':
                break
            
            sock.sendall((cmd + "\r\n").encode())
            
            # Pentru DATA, citim până la "." pentru terminare
            if cmd.upper() == 'DATA':
                response = sock.recv(1024).decode()
                print(f"S: {response.strip()}")
                if response.startswith('354'):
                    print("[INFO] Introduceți mesajul. Linie cu doar '.' pentru a termina.")
                    while True:
                        line = input()
                        sock.sendall((line + "\r\n").encode())
                        if line == '.':
                            break
            
            response = sock.recv(4096).decode()
            for line in response.strip().split('\n'):
                print(f"S: {line.strip()}")
            
            if cmd.upper() == 'QUIT':
                break
        
        sock.close()
        
    except Exception as e:
        print(f"[ERR] {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Client SMTP Didactic pentru Săptămâna 12",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple de utilizare:

  # Trimitere simplă
  python3 smtp_client.py --host 127.0.0.1 --port 1025 \\
      --from sender@test.local --to recipient@test.local \\
      --subject "Test S12" --body "Aceasta este o testare."

  # Mod interactiv (pentru învățare)
  python3 smtp_client.py --host 127.0.0.1 --port 1025 --interactive

  # Cu debugging verbose
  python3 smtp_client.py --host 127.0.0.1 --port 1025 \\
      --from a@b --to c@d --subject "Test" --body "Test" -v

Revolvix&Hypotheticalandrei
        """
    )
    
    parser.add_argument('--host', default='127.0.0.1',
                        help='Hostname serverului SMTP (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=1025,
                        help='Portul SMTP (default: 1025)')
    parser.add_argument('--from', dest='sender', default='sender@test.local',
                        help='Adresa expeditorului')
    parser.add_argument('--to', dest='recipient', default='recipient@test.local',
                        help='Adresa destinatarului')
    parser.add_argument('--subject', default='Test S12',
                        help='Subiectul mesajului')
    parser.add_argument('--body', default='Mesaj de test din Săptămâna 12.',
                        help='Corpul mesajului')
    parser.add_argument('--tls', action='store_true',
                        help='Folosește STARTTLS')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Mod interactiv (comenzi manuale)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Output verbose')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode(args.host, args.port)
    else:
        success = send_email(
            host=args.host,
            port=args.port,
            sender=args.sender,
            recipients=[args.recipient],
            subject=args.subject,
            body=args.body,
            use_tls=args.tls,
            verbose=args.verbose
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
