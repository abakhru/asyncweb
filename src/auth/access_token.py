from datetime import datetime, timedelta

from jwt import JWT, jwk_from_pem
from jwt.utils import get_int_from_datetime

from src import APP_HOME
from src.conf import config

secret_key = config['project']['secret']


class AccessToken:
    def __init__(self):
        self.__instance = JWT()
        self.__algorithm = "RS256"
        self.__signing_key = jwk_from_pem(APP_HOME.joinpath('src', 'auth',
                                                            'jwtRS256_private.pem').read_bytes())
        self.__verifying_key = jwk_from_pem(APP_HOME.joinpath('src', 'auth',
                                                              'jwtRS256_public.pem').read_bytes())

    def create_access_token(self, *, data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"ist": get_int_from_datetime(datetime.utcnow())})
        to_encode.update({"exp": get_int_from_datetime(expire)})
        encoded_jwt = self.__instance.encode(to_encode, self.__signing_key, self.__algorithm)
        return encoded_jwt

    def decode_access_token(self, *, token: str) -> dict:
        return self.__instance.decode(token, self.__verifying_key, do_time_check=False)

    def generate_password_reset_token(self, email: str) -> str:
        delta = timedelta(hours=config['email']['email_reset_token_expire_hours'])
        now = datetime.utcnow()
        expires = now + delta
        exp = expires.timestamp()
        encoded_jwt = self.__instance.encode(
            {"exp": exp, "ist": now, "sub": email},
            self.__signing_key,
            alg=self.__algorithm,
        )
        return encoded_jwt

    def verify_password_reset_token(self, token: str) -> dict:
        return self.__instance.decode(token, self.__verifying_key, do_time_check=False)


access_token = AccessToken()
