FROM python:3.11-alpine

RUN pip install --no-cache-dir pyftpdlib

WORKDIR /app
COPY ftp_server.py .

# Creare structură directoare FTP
RUN mkdir -p /home/ftp/uploads /home/ftp/downloads && \
    echo "Bine ați venit la serverul FTP - Săptămâna 10!" > /home/ftp/welcome.txt && \
    echo "Revolvix&Hypotheticalandrei" >> /home/ftp/welcome.txt

EXPOSE 2121
EXPOSE 30000-30009

CMD ["python3", "ftp_server.py"]
