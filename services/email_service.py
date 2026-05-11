import os
import mailtrap as mt

from dotenv import load_dotenv

load_dotenv()


MAILTRAP_TOKEN = os.getenv("MAILTRAP_TOKEN")
EMAIL_FROM = os.getenv("EMAIL_FROM")


def send_invitation_email(
    email_destino: str,
    codigo: str,
    rol: str
):

    mail = mt.Mail(
        sender=mt.Address(
            email=EMAIL_FROM,
            name="UrbanNexus"
        ),

        to=[
            mt.Address(email=email_destino)
        ],

        subject="Invitación UrbanNexus",

        text=f"""
Hola.

Has recibido una invitación para UrbanNexus.

Rol asignado: {rol}

Código de invitación:
{codigo}

Utiliza este código durante el registro.
"""
    )

    client = mt.MailtrapClient(token=MAILTRAP_TOKEN)

    client.send(mail)