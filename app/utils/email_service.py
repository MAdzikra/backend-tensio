from flask_mail import Message
from flask import current_app
from app.extensions import mail
import requests
import resend

def send_email(subject, recipients, body, html):

    resend.api_key = current_app.config["RESEND_API_KEY"]

    try:
        resend.Emails.send({
            "from": "Tensio <noreply@tensio.my.id>",
            "to": recipients,
            "subject": subject,
            "html": html
        })

        print("Email sent successfully")

    except Exception as e:
        print("Email failed:", str(e))

# def send_email(subject, recipients, body, html):
    
#     msg = Message(
#         subject=subject,
#         recipients=recipients,
#         body=body,
#         html=html,
#         sender=current_app.config["MAIL_DEFAULT_SENDER"]
#     )
#     try:
#         mail.send(msg)
#         print("Email sent successfully")
#     except Exception as e:
#         print("Email failed:", str(e))

# def send_email(subject, recipients, body, html):
#     api_key = current_app.config["BREVO_API_KEY"]
#     print("=== DEBUG EMAIL ===")
#     print("API KEY EXISTS:", bool(api_key))
#     print("SENDER:", current_app.config.get("MAIL_DEFAULT_SENDER"))
#     print("RECIPIENT:", recipients)
#     print("SUBJECT:", subject)
#     url = "https://api.brevo.com/v3/smtp/email"

#     payload = {
#         "sender": {
#             "name": "Tensio",
#             "email": current_app.config["MAIL_DEFAULT_SENDER"]
#         },
#         "to": [{"email": recipients[0]}],
#         "subject": subject,
#         "htmlContent": html
#     }
#     print("PAYLOAD:", payload)

#     headers = {
#         "accept": "application/json",
#         "api-key": api_key,
#         "content-type": "application/json"
#     }

#     try:
#         response = requests.post(
#             url,
#             json=payload,
#             headers=headers,
#             timeout=10
#         )

#         print(response.status_code)
#         print(response.text)

#     except Exception as e:
#         print("Email failed:", str(e))


def send_verification_email(user_email, token):
    frontend_url = current_app.config["FRONTEND_URL"]
    verify_link = f"{frontend_url}/verify-email?token={token}"

    subject = "Verify Your Tensio Account"

    body = f"""
    Halo,

    Terima kasih telah mendaftar di Tensio.

    Silakan buka link berikut untuk memverifikasi akun Anda:
    {verify_link}

    Link ini berlaku selama 1 jam.

    Jika Anda tidak merasa mendaftar, abaikan email ini.
    """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Verifikasi Akun</title>
    </head>
    <body style="
        margin:0;
        padding:0;
        background-color:#F3F4F6;
        font-family:Arial, sans-serif;
    ">

    <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 20px;">
        <tr>
        <td align="center">

            <table width="600" cellpadding="0" cellspacing="0" style="
                background:white;
                border-radius:16px;
                overflow:hidden;
                box-shadow:0 4px 20px rgba(0,0,0,0.08);
            ">

            <!-- Header -->
            <tr>
                <td style="
                    background:linear-gradient(135deg,#2563EB,#3B82F6);
                    padding:40px;
                    text-align:center;
                ">
                <h1 style="
                    color:white;
                    margin:0;
                    font-size:28px;
                ">
                    Tensio
                </h1>

                <p style="
                    color:#DBEAFE;
                    margin-top:10px;
                    font-size:16px;
                ">
                    Sistem Skrining Risiko Hipertensi
                </p>
                </td>
            </tr>

            <!-- Content -->
            <tr>
                <td style="padding:40px;">

                <h2 style="
                    color:#111827;
                    margin-top:0;
                ">
                    Verifikasi Akun Anda
                </h2>

                <p style="
                    color:#4B5563;
                    line-height:1.8;
                    font-size:15px;
                ">
                    Halo,
                </p>

                <p style="
                    color:#4B5563;
                    line-height:1.8;
                    font-size:15px;
                ">
                    Terima kasih telah mendaftar di <b>Tensio</b>.
                    Klik tombol di bawah untuk memverifikasi akun Anda.
                </p>

                <!-- Button -->
                <table cellpadding="0" cellspacing="0" style="margin:30px auto;">
                    <tr>
                    <td align="center" bgcolor="#2563EB" style="
                        border-radius:10px;
                    ">
                        <a href="{verify_link}" style="
                            display:inline-block;
                            padding:14px 28px;
                            color:white;
                            text-decoration:none;
                            font-weight:bold;
                            font-size:15px;
                        ">
                        Verifikasi Akun
                        </a>
                    </td>
                    </tr>
                </table>

                <p style="
                    color:#6B7280;
                    font-size:14px;
                    line-height:1.7;
                ">
                    Link ini berlaku selama <b>1 jam</b>.
                </p>

                <p style="
                    color:#6B7280;
                    font-size:14px;
                    line-height:1.7;
                ">
                    Jika tombol tidak bekerja, copy link berikut:
                </p>

                <p style="
                    word-break:break-all;
                    color:#2563EB;
                    font-size:13px;
                ">
                    {verify_link}
                </p>

                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td style="
                    background:#F9FAFB;
                    padding:24px;
                    text-align:center;
                ">
                <p style="
                    margin:0;
                    color:#9CA3AF;
                    font-size:12px;
                ">
                    © 2026 Tensio. All rights reserved.
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

    send_email(subject, [user_email], body, html)


def send_reset_password_email(user_email, token):
    frontend_url = current_app.config["FRONTEND_URL"]
    reset_link = f"{frontend_url}/reset-password?token={token}"

    subject = "Reset Password Tensio"

    body = f"""
    Halo,

    Kami menerima permintaan reset password untuk akun Tensio Anda.

    Silakan buka link berikut untuk membuat password baru:
    {reset_link}

    Link ini berlaku selama 1 jam.

    Jika ini bukan Anda, abaikan email ini.
    """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Reset Password</title>
    </head>
    <body style="
        margin:0;
        padding:0;
        background-color:#F3F4F6;
        font-family:Arial, sans-serif;
    ">

    <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 20px;">
        <tr>
        <td align="center">

            <table width="600" cellpadding="0" cellspacing="0" style="
                background:white;
                border-radius:16px;
                overflow:hidden;
                box-shadow:0 4px 20px rgba(0,0,0,0.08);
            ">

            <!-- Header -->
            <tr>
                <td style="
                    background:linear-gradient(135deg,#2563EB,#3B82F6);
                    padding:40px;
                    text-align:center;
                ">
                <h1 style="
                    color:white;
                    margin:0;
                    font-size:28px;
                ">
                    Tensio
                </h1>

                <p style="
                    color:#DBEAFE;
                    margin-top:10px;
                    font-size:16px;
                ">
                    Sistem Skrining Risiko Hipertensi
                </p>
                </td>
            </tr>

            <!-- Content -->
            <tr>
                <td style="padding:40px;">

                <h2 style="
                    color:#111827;
                    margin-top:0;
                ">
                    Reset Password
                </h2>

                <p style="
                    color:#4B5563;
                    line-height:1.8;
                    font-size:15px;
                ">
                    Halo,
                </p>

                <p style="
                    color:#4B5563;
                    line-height:1.8;
                    font-size:15px;
                ">
                    Kami menerima permintaan reset password akun <b>Tensio</b>.
                    Klik tombol di bawah untuk mereset password akun Anda.
                </p>

                <!-- Button -->
                <table cellpadding="0" cellspacing="0" style="margin:30px auto;">
                    <tr>
                    <td align="center" bgcolor="#2563EB" style="
                        border-radius:10px;
                    ">
                        <a href="{reset_link}" style="
                            display:inline-block;
                            padding:14px 28px;
                            color:white;
                            text-decoration:none;
                            font-weight:bold;
                            font-size:15px;
                        ">
                        Verifikasi Akun
                        </a>
                    </td>
                    </tr>
                </table>

                <p style="
                    color:#6B7280;
                    font-size:14px;
                    line-height:1.7;
                ">
                    Link ini berlaku selama <b>1 jam</b>.
                </p>

                <p style="
                    color:#6B7280;
                    font-size:14px;
                    line-height:1.7;
                ">
                    Jika tombol tidak bekerja, copy link berikut:
                </p>

                <p style="
                    word-break:break-all;
                    color:#2563EB;
                    font-size:13px;
                ">
                    {reset_link}
                </p>

                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td style="
                    background:#F9FAFB;
                    padding:24px;
                    text-align:center;
                ">
                <p style="
                    margin:0;
                    color:#9CA3AF;
                    font-size:12px;
                ">
                    © 2026 Tensio. All rights reserved.
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

    send_email(subject, [user_email], body, html)