from login_service import LoginService
import json
from logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


def login(username, password, callback_url) -> tuple[dict, dict]:
    login_service = LoginService(callback_url)
    login_service.login(username, password)
    return login_service.get_cookies(), login_service.get_params()


if __name__ == "__main__":
    username = None
    password = None
    callback_url = None
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
            username = settings["username"]
            password = settings["password"]
            try:
                callback_url = settings["callback_url"]
            except:
                callback_url = None
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")


    if username is None:
        username = input("请输入学号: ")
    if password is None:
        password = input("请输入密码: ")

    try:
        cookies, params = login(username, password, callback_url)

        with open("settings.json", "w") as f:
            json.dump(
                {
                    "username": username,
                    "password": password,
                    "callback_url": callback_url if callback_url else "",
                },
                f,
                indent=4,
            )
        with open("output/cookies.json", "w") as f:
            json.dump(cookies, f, indent=4)
        with open("output/params.json", "w") as f:
            json.dump(params, f, indent=4)
        logger.info("登录成功")
    except Exception as e:
        logger.error(f"登录失败: {e}")
        exit(1)
