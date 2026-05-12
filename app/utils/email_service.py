from flask_mail import Message
from flask import current_app
from app.extensions import mail


def send_email(subject, recipients, body, html):
    msg = Message(
        subject=subject,
        recipients=recipients,
        body=body,
        html=html,
        sender=current_app.config["MAIL_DEFAULT_SENDER"]
    )
    try:
        mail.send(msg)
        print("Email sent successfully")
    except Exception as e:
        print("Email failed:", str(e))


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
    <h2>Verifikasi Akun Tensio</h2>
    <p>Halo,</p>
    <p>Terima kasih telah mendaftar di <b>Tensio</b>.</p>
    <p>Silakan klik tombol di bawah untuk memverifikasi akun Anda:</p>
    <p>
        <a href="{verify_link}" 
           style="background:#2563EB;color:white;padding:12px 20px;text-decoration:none;border-radius:8px;">
           Verifikasi Akun
        </a>
    </p>
    <p>Link ini berlaku selama <b>1 jam</b>.</p>
    <p>Jika Anda tidak merasa mendaftar, abaikan email ini.</p>
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
    <h2>Reset Password Tensio</h2>
    <p>Halo,</p>
    <p>Kami menerima permintaan reset password untuk akun Anda.</p>
    <p>Silakan klik tombol di bawah untuk membuat password baru:</p>
    <p>
        <a href="{reset_link}" 
           style="background:#DC2626;color:white;padding:12px 20px;text-decoration:none;border-radius:8px;">
           Reset Password
        </a>
    </p>
    <p>Link ini berlaku selama <b>1 jam</b>.</p>
    <p>Jika ini bukan Anda, abaikan email ini.</p>
    """

    send_email(subject, [user_email], body, html)