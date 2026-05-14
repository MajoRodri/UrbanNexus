import os
import ssl
import smtplib
import base64

from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send_invitation_email(
    email_destino: str,
    codigo: str,
    rol: str,
    nombres: str,
    apellidos: str
):
    cuerpo = (
        f"Hola {nombres} {apellidos}.\n\n"
        f"Has recibido una invitacion para registrarte en UrbanNexus.\n\n"
        f"Rol asignado: {rol}\n\n"
        f"Codigo de invitacion:\n{codigo}\n\n"
        f"Utiliza este codigo en el formulario de registro para completar tu alta.\n\n"
        f"Este codigo es personal, de un solo uso y tiene fecha de caducidad.\n\n"
        f"Un saludo,\nEquipo UrbanNexus\n"
    )

    body_b64 = base64.b64encode(cuerpo.encode("utf-8")).decode("ascii")

    raw = "\r\n".join([
        f"From: UrbanNexus <{GMAIL_USER}>",
        f"To: {email_destino}",
        "Subject: Invitacion UrbanNexus",
        "MIME-Version: 1.0",
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: base64",
        "",
        body_b64,
    ])

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as servidor:
        servidor.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        servidor.sendmail(GMAIL_USER, [email_destino], raw.encode("ascii"))
