from typing import Optional

__all__ = [
    "OIAnalyticsAPICredentials",
    "set_default_oianalytics_credentials",
    "get_default_oianalytics_credentials",
]


# Base class for credentials
class OIAnalyticsAPICredentials:
    def __init__(
        self,
        base_url: str,
        login: Optional[str] = None,
        pwd: Optional[str] = None,
        token: Optional[str] = None,
    ):
        if login is not None and pwd is not None:
            self.auth_type = "Basic"
        elif token is not None:
            self.auth_type = "Token"
        else:
            raise ValueError("Either login/password or token should be provided")
        self.base_url = base_url.strip("/")
        self.login = login
        self.pwd = pwd
        self.token = token

    def __repr__(self):
        if self.auth_type == "Basic":
            auth_summary = f"Login: {self.login}\nPassword: {self.pwd}"
        elif self.auth_type == "Token":
            auth_summary = f"Token: {self.token}"
        else:
            raise ValueError(
                "The only supported authentication types are Basic or Token"
            )
        return f"{self.auth_type} authentication on {self.base_url}\n{auth_summary}"

    @property
    def auth_kwargs(self):
        if self.auth_type == "Basic":
            return {"auth": (self.login, self.pwd)}
        elif self.auth_type == "Token":
            return {"headers": {"Authorization": f"Bearer {self.token}"}}

    def set_as_default_credentials(self):
        set_default_oianalytics_credentials(credentials=self)


# Init
DEFAULT_CREDENTIALS = None


# Default credentials management
def set_default_oianalytics_credentials(
    credentials: Optional[OIAnalyticsAPICredentials] = None,
    base_url: Optional[str] = None,
    login: Optional[str] = None,
    pwd: Optional[str] = None,
    token: Optional[str] = None,
):
    global DEFAULT_CREDENTIALS

    if isinstance(credentials, OIAnalyticsAPICredentials):
        DEFAULT_CREDENTIALS = credentials
    else:
        DEFAULT_CREDENTIALS = OIAnalyticsAPICredentials(
            base_url=base_url, login=login, pwd=pwd, token=token
        )


def get_default_oianalytics_credentials():
    global DEFAULT_CREDENTIALS
    return DEFAULT_CREDENTIALS
