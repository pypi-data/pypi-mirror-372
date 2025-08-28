class OdooLauncherException(Exception):
    pass


class MissingDBCredential(OdooLauncherException):
    def __init__(self) -> None:
        super(MissingDBCredential, self).__init__()
        self.msg = """Can't start Odoo without a db name
        Please add the one of the following environment variable
        - DATABASE
        - DB_NAME
        - POSTGRESQL_ADDON_DB""".lstrip()
