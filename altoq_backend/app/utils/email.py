import os
import requests
from ..config import settings


def send_recovery_email(email: str, code: str) -> bool:
    """
    Sends a recovery email with a 6-digit code using the Resend API.
    If credentials are missing, it falls back to printing the code for local development.
    """
    # Load Resend credentials from settings
    api_key = settings.resend_api_key
    email_from = settings.email_from

    # Build the HTML email body
    subject = "Código de recuperación de contraseña - AltoQ"
    html_content = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <style>
            body {{font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background:#f3f4f6; color:#1f2937; margin:0; padding:0;}}
            .container {{max-width:550px; margin:40px auto; background:#fff; border-radius:16px; box-shadow:0 10px 15px -3px rgba(0,0,0,0.05),0 4px 6px -2px rgba(0,0,0,0.05); border:1px solid #e5e7eb;}}
            .header {{background:linear-gradient(135deg, #1e40af, #3b82f6); padding:32px 24px; text-align:center;}}
            .header h1 {{color:#fff; margin:0; font-size:26px; font-weight:800;}}
            .content {{padding:40px 32px;}}
            .content p {{font-size:16px; line-height:1.6; color:#4b5563; margin:0 0 24px;}}
            .code-box {{text-align:center; background:#f8fafc; border:2px dashed #3b82f6; border-radius:12px; padding:20px; margin:24px 0;}}
            .code {{font-size:36px; font-weight:800; color:#1e3a8a; letter-spacing:8px; font-family:'Courier New',Courier,monospace;}}
            .warning {{font-size:13px; color:#9ca3af; text-align:center; margin-top:24px; line-height:1.4;}}
            .footer {{background:#f9fafb; padding:24px; text-align:center; border-top:1px solid #f3f4f6;}}
            .footer p {{font-size:12px; color:#9ca3af; margin:0;}}
        </style>
    </head>
    <body>
        <div style="display:none;max-height:0;overflow:hidden;font-size:1px;color:#fff;line-height:1px;">
            Recupera tu contraseña en AltoQ de forma segura.
        </div>
        <div class="container">
            <div class="header">
                <h1>AltoQ Marketplace</h1>
                <p>Hola,</p>
                <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en AltoQ. Usa el siguiente código de verificación de un solo uso para continuar:</p>
            </div>
            <div class="content">
                <div class="code-box">
                    <div class="code">{code}</div>
                </div>
                <p>Este código es válido por <strong>15 minutos</strong>. Si tú no realizaste esta solicitud, puedes ignorar este mensaje con total seguridad; tu contraseña actual seguirá siendo la misma.</p>
                <div class="warning">
                    Este código es confidencial. Nunca compartas este código con nadie. El equipo de AltoQ nunca te pedirá este código.
                </div>
            </div>
            <div class="footer">
                <p>&copy; 2026 AltoQ. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # If any credential is missing, fallback to development print
    if not api_key:
        print("\n" + "="*80)
        print("  [ALTOQ DEVELOPMENT] CODIGO DE RECUPERACION DE CONTRASEÑA (RESEND NO CONFIGURADO)")
        print(f"  Para el usuario: {email}")
        print(f"  El codigo es   : {code}")
        print("="*80 + "\n")
        return True

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": email_from,
            "to": [email],
            "subject": subject,
            "html": html_content
        }

        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code in (200, 201):
            print("Correo de recuperación enviado con éxito vía Resend.")
            return True
        else:
            print(f"Error al enviar correo vía Resend. Status: {response.status_code}, Response: {response.text}")
            raise Exception(response.text)

    except Exception as e:
        print(f"Excepción al enviar correo vía Resend: {e}")
        # Fallback de desarrollo en caso de error de red o API
        print("\n" + "="*80)
        print("  [ALTOQ FALLBACK] CODIGO DE RECUPERACION (ERROR CONEXION RESEND)")
        print(f"  Para el usuario: {email}")
        print(f"  El codigo es   : {code}")
        print("="*80 + "\n")
        return False
