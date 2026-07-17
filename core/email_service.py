from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER, MAIL_FROM_NAME, USE_CREDENTIALS, VERIFICATION_TOKEN_EXPIRE_MINUTES, MAIL_STARTTLS, MAIL_SSL_TLS
from fastapi_mail.schemas import MessageType
from starlette.datastructures import UploadFile
from core.barcode_service import generate_barcode_image
from io import BytesIO

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

async def send_employee_barcode_to_owner(owner_email: str, employee_name: str, employee_username: str, barcode_code: str):

    barcode_buffer: BytesIO = generate_barcode_image(barcode_code)

    attachment = UploadFile(
        filename=f"barcode_{employee_username}.png",
        file=barcode_buffer,
    )

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="
        margin:0;
        padding:0;
        background:#f4f4f4;
        font-family:Arial, Helvetica, sans-serif;
    ">

        <table width="100%" cellpadding="30">
            <tr>
                <td align="center">

                    <table width="600"
                           cellpadding="30"
                           cellspacing="0"
                           style="
                               background:#ffffff;
                               border-radius:10px;
                               box-shadow:0 2px 10px rgba(0,0,0,.08);
                           ">

                        <tr>
                            <td>

                                <h2 style="margin-top:0;">
                                    Nuevo código de barras generado
                                </h2>

                                <p>
                                    Se ha registrado un nuevo colaborador en ERM.
                                </p>

                                <table cellpadding="6">

                                    <tr>
                                        <td><strong>Nombre</strong></td>
                                        <td>{employee_name}</td>
                                    </tr>

                                    <tr>
                                        <td><strong>Usuario</strong></td>
                                        <td>{employee_username}</td>
                                    </tr>

                                    <tr>
                                        <td><strong>Código</strong></td>
                                        <td style="
                                            font-family:monospace;
                                            font-size:16px;
                                        ">
                                            {barcode_code}
                                        </td>
                                    </tr>

                                </table>

                                <br>

                                <p>
                                    El código de barras se encuentra adjunto a este
                                    correo en formato PNG.
                                </p>

                                <p>
                                    Imprímalo y entrégueselo al colaborador para
                                    utilizarlo en el sistema de inventario.
                                </p>

                                <hr>

                                <p style="
                                    color:#777;
                                    font-size:12px;
                                ">
                                    © 2026 ERM System
                                </p>

                            </td>
                        </tr>

                    </table>

                </td>
            </tr>
        </table>

    </body>
    </html>
    """

    message = MessageSchema(
        subject=f"Código de barras - {employee_name}",
        recipients=[owner_email],
        body=html_body,
        subtype=MessageType.html,
        attachments=[attachment],
    )

    fm = FastMail(conf)
    await fm.send_message(message)