from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER, MAIL_FROM_NAME, USE_CREDENTIALS, VERIFICATION_TOKEN_EXPIRE_MINUTES, MAIL_STARTTLS, MAIL_SSL_TLS

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    USE_CREDENTIALS=USE_CREDENTIALS,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS
)

async def send_verification_email(recipient: str, verification_code: str):
    html_body = f"""
    <html>
      <body style="margin:0; padding:0; background-color:#121212; font-family: 'Inter', sans-serif; color:#ffffff;">
        <div style="max-width:600px; margin:50px auto; padding:30px; background-color:#1E1E1E; border-radius:10px; text-align:center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
          
          <h1 style="font-size:28px; font-weight:bold; color:#ffffff; margin-bottom:10px;">Verificación de Email</h1>
          <p style="font-size:16px; color:#bbbbbb; margin-bottom:30px;">
            Gracias por registrarte. Usa el siguiente código para verificar tu dirección de correo:
          </p>
          
          <div style="display:inline-block; padding:20px 40px; font-size:24px; font-weight:bold; color:#121212; background-color:#00b894; border-radius:8px; letter-spacing:2px; margin-bottom:30px;">
            {verification_code}
          </div>
          
          <p style="font-size:14px; color:#777777;">
            Este código expirará en {VERIFICATION_TOKEN_EXPIRE_MINUTES} minutos.
          </p>
          
          <p style="font-size:12px; color:#555555; margin-top:40px;">
            &copy; 2026 ERM System. Todos los derechos reservados.
          </p>
        </div>
      </body>
    </html>
    """

    message = MessageSchema(
        subject="Verification Email for FM ERM",
        recipients=[recipient],
        body=html_body,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)