import os
import mailtrap as mt

from dotenv import load_dotenv

load_dotenv()


MAILTRAP_TOKEN = os.getenv("MAILTRAP_TOKEN")
EMAIL_FROM = os.getenv("EMAIL_FROM")


def send_invitation_email(
    email_destino: str,
    codigo: str,
    rol: str,
    nombres: str,
    apellidos: str
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
Hola {nombres} {apellidos}.

Has recibido una invitación para registrarte en UrbanNexus.

Rol asignado: {rol}

Código de invitación:
{codigo}

Utiliza este código en el formulario de registro para completar tu alta.

Este código es personal, de un solo uso y tiene fecha de caducidad.

Un saludo,
Equipo UrbanNexus
"""
    )

    client = mt.MailtrapClient(token=MAILTRAP_TOKEN)

    client.send(mail)