import os
import resend

def send_recovery_email(email: str, code: str) -> bool:
    """
    Sends a recovery email with a 6-digit code using the Resend Python SDK.
    If RESEND_API_KEY is not configured, it prints the code to the terminal for development.
    """
    api_key = os.getenv("RESEND_API_KEY", "re_Pk6ziFWG_JSGZLkyM2wf64pZHYjWYFxs3")
    resend.api_key = api_key

    # Sandbox requirement: sender must be onboarding@resend.dev unless domain is verified
    from_email = os.getenv("EMAIL_FROM", "onboarding@resend.dev")
    subject = "Código de recuperación de contraseña - AltoQ"

    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                background-color: #f3f4f6;
                color: #1f2937;
                margin: 0;
                padding: 0;
                -webkit-font-smoothing: antialiased;
            }}
            .container {{
                max-width: 550px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 16px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                overflow: hidden;
                border: 1px solid #e5e7eb;
            }}
            .header {{
                background: linear-gradient(135deg, #1e40af, #3b82f6);
                padding: 32px 24px;
                text-align: center;
            }}
            .header h1 {{
                color: #ffffff;
                margin: 0;
                font-size: 26px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }}
            .content {{
                padding: 40px 32px;
            }}
            .content p {{
                font-size: 16px;
                line-height: 1.6;
                color: #4b5563;
                margin-top: 0;
                margin-bottom: 24px;
            }}
            .code-box {{
                text-align: center;
                background: #f8fafc;
                border: 2px dashed #3b82f6;
                border-radius: 12px;
                padding: 20px;
                margin: 24px 0;
            }}
            .code {{
                font-size: 36px;
                font-weight: 800;
                color: #1e3a8a;
                letter-spacing: 8px;
                font-family: 'Courier New', Courier, monospace;
            }}
            .warning {{
                font-size: 13px;
                color: #9ca3af;
                text-align: center;
                margin-top: 24px;
                line-height: 1.4;
            }}
            .footer {{
                background-color: #f9fafb;
                padding: 24px;
                text-align: center;
                border-top: 1px solid #f3f4f6;
            }}
            .footer p {{
                font-size: 12px;
                color: #9ca3af;
                margin: 0;
            }}
        </style>
    </head>
    <body>
        <!-- Hidden preheader text to prevent the recovery code from appearing in email previews -->
        <div style="display: none; max-height: 0px; overflow: hidden; font-size: 1px; color: #fff; line-height: 1px;">
            Recupera tu contraseña en AltoQ de forma segura.
        </div>
        <div style="display: none; max-height: 0px; overflow: hidden; font-size: 1px; color: #fff; line-height: 1px;">
            &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
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

    try:
        print(f"Sending recovery email to {email} via Resend SDK...")
        res = resend.Emails.send({
            "from": from_email,
            "to": email,
            "subject": subject,
            "html": html_content
        })
        print(f"Resend send response: {res}")
        return True
    except Exception as e:
        print(f"Error sending recovery email to {email} via Resend: {e}")
        # Local development fallback output
        print("\n" + "=" * 80)
        print(f"  [ALTOQ FALLBACK / DEVELOPMENT] CODIGO DE RECUPERACION DE CONTRASEÑA")
        print(f"  Para el usuario: {email}")
        print(f"  El codigo es   : {code}")
        print("=" * 80 + "\n")
        return False

