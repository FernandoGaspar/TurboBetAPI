import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtpout.secureserver.net"
SMTP_PORT = 465
EMAIL_ADDRESS = "administracao@helpmebr.com.br"
EMAIL_PASSWORD = "932TSk^Kz4~O"

def enviar_email(destinatario, assunto, corpo):
    msg = EmailMessage()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.set_content(corpo)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# enviar_email("marcos.pereira291@gmail.com", "Teste email", "AGORA VAI CARAIOOO")
