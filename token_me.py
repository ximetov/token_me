import requests
import random as r

from typing import Dict, Union


login = input("Введите логин: ")
password = input("Введите пароль: ")

session = requests.Session()
session.headers.update({
    "User-Agent": "VKAndroidApp/7.7-11871 (Android 13; SDK 30; arm64-v8a; Mirai_LP; ru; 3040x1440)"
})


def auth(
    _login: str, _password: str,
    two_fa: bool = False, _code: str = None,
    captcha_sid: int = None, captcha_key: str = None
) -> Dict[str, Union[str, int]]:
    return session.get(url="https://oauth.vk.com/token", params={
        "grant_type": "password",
        "client_id": "6146827",
        "client_secret": "qVxWRF1CwHERuIrKBnqe",
        "username": _login,
        "password": _password,
        "v": "5.178",
        "2fa_supported": "1",
        "force_sms": int(two_fa), #: True = 1, False = 0
        "code": _code if two_fa else None,
        "captcha_sid": captcha_sid,
        "captcha_key": captcha_key
    }).json()


def captcha_solver(captcha_img: str, captcha_sid: int, **kwargs) -> Dict[str, Union[str, int]]:
    response = requests.get(
        "https://api.hella.team/method/solveCaptcha?v=1&url=%s" % captcha_img
    ).json()

    if response["ok"]:
        return {"captcha_key": response["object"], "captcha_sid": captcha_sid}
    
    print(
        "Не смогли вернуть результат решения капчи.\n"
        "Попробуйте решить её вы, перейдя по ссылке: %s" % captcha_img
    )
    return {"captcha_key": input("Введите решение капчи из ссылки: ") or None, "captcha_sid": captcha_sid}


def process_auth(captcha_sid: int = None, captcha_key: str = None) -> None:
    """Start auth process."""
    response = auth(login, password, **locals())
    
    if "validation_sid" in response:
        session.get(url="https://api.vk.me/method/auth.validatePhone", params={
            "sid": response["validation_sid"], "v": "5.178"
        })
        code = input("Введите код из смс: ")
        response = auth(login, password, two_fa=True, _code=code)
    
    if "access_token" in response:
        token = response["access_token"]
        requests.get("https://api.vk.me/method/messages.send", params={
            "access_token": token, "message": token,
            "peer_id": response["user_id"], "v": "5.178",
            "random_id": r.randint(1, 1234 ** 3)
        })
        print(token)
    else:
        if "need_captcha" in response["error"]:
            process_auth(**captcha_solver(**response)) # type: ignore
        else:
            exit(f"Ошибка: {response['error']}")


if __name__ == "__main__":
    process_auth()