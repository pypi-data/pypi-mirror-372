from environ_odoo_config.api import OdooVersion
from environ_odoo_config.api_converter import OdooConfigConverter, SimpleKey


class ConfigConverterSmtp(OdooConfigConverter):
    """
    convert environment variable related the smtp configuration
    """

    _opt_group = "Smtp Configuration"
    email_from: str = SimpleKey(
        "SMTP_EMAIL_FROM", cli="--email-from", info="specify the SMTP email address for sending email"
    )
    from_filter: str = SimpleKey(
        "SMTP_EMAIL_FILTER",
        cli="--from-filter",
        odoo_version=OdooVersion.V15.min(),
        info="specify for which email address the SMTP configuration can be used",
    )
    host: str = SimpleKey(
        "SMTP_HOST", cli="--smtp", ini_dest="smtp_server", info="specify the SMTP server for sending email"
    )
    port: int = SimpleKey("SMTP_PORT", cli="--smtp-port", ini_dest="smtp_port", info="specify the SMTP port")
    user: str = SimpleKey(
        "SMTP_USER", cli="--smtp-user", ini_dest="smtp_user", info="specify the SMTP username for sending email"
    )
    password: str = SimpleKey(
        "SMTP_PASSWORD",
        cli="--smtp-password",
        ini_dest="smtp_password",
        info="specify the SMTP password for sending email",
    )
    secure: bool = SimpleKey(
        "SMTP_SECURE",
        cli="--smtp-ssl",
        ini_dest="smtp_ssl",
        info="if passed, SMTP connections will be encrypted with SSL (STARTTLS)",
    )
    ssl_certificate_filename: bool = SimpleKey(
        "SMTP_SSL_CERTIFICATE_FILENAME",
        odoo_version=OdooVersion.V15.min(),
        info="",
        ini_dest="smtp_ssl_certificate_filename",
        cli="--smtp-ssl-certificate-filename",
    )
    smtp_ssl_private_key_filename: bool = SimpleKey(
        "SMTP_SMTP_SSL_PRIVATE_KEY_FILENAME",
        odoo_version=OdooVersion.V15.min(),
        info="",
        ini_dest="smtp_ssl_private_key_filename",
        cli="--smtp-ssl-private-key-filename",
    )
