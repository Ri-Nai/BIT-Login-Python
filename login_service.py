import re
import requests
import ddddocr
from aes_util import encrypt_password
from logger import LoggerFactory, LogParser

logger = LoggerFactory.get_logger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

BASE_URL = "https://login.bit.edu.cn"
LOGIN_URL = f"{BASE_URL}/authserver/login"

class LoginService:
    def __init__(self, service_url: str):
        self.service_url = service_url
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.session.verify = False
        self.login_params = {}
        self.ocr = ddddocr.DdddOcr(show_ad=False)

        self._error_pattern = re.compile(r'<span id="showErrorTip"><span>(.*?)</span>')
        self._execution_pattern = re.compile(r'<input type="hidden" id="execution" name="execution" value="(.*?)"(.*?)>')
        self._pwd_encrypt_salt_pattern = re.compile(r'<input type="hidden" id="pwdEncryptSalt" value="(.*?)"(.*?)>')
    
    def _get_html_error(self, html: str) -> str:
        match = self._error_pattern.search(html)
        return match.group(1) if match else ""

    def _get_login_params(self) -> tuple[str, str]:
        try:
            response = self.session.get(
                LOGIN_URL,
                params={"service": self.service_url}
            )
            if not response.ok:
                raise RuntimeError(f"获取登录页面失败: {response.status_code}")
            html = response.text
            try:
                execution = self._execution_pattern.search(html).group(1)
                print(f"execution: {execution}")
                pwd_encrypt_salt = self._pwd_encrypt_salt_pattern.search(html).group(1)
                print(f"pwd_encrypt_salt: {pwd_encrypt_salt}")
                return execution, pwd_encrypt_salt
            except Exception as e:
                raise RuntimeError("找不到登录参数")

        except Exception as e:
            logger.error(f"获取登录参数失败: {str(e)}")
            raise

    def check_need_captcha(self, username: str) -> bool:
        response = self.session.get(
            f"{BASE_URL}/authserver/checkNeedCaptcha.htl",
            params={"username": username}
        )
        if response.text == '{"isNeed":true}':
            logger.info(f"需要验证码: {username}")
            return True
        else:
            return False

    def _get_captcha(self) -> str:
        try:
            response = self.session.get(
                f"{BASE_URL}/authserver/getCaptcha.htl",
            )
            if not response.ok:
                raise RuntimeError(f"获取验证码失败: {response.status_code}")

            with open("output/captcha.jpg", "wb") as f:
                f.write(response.content)
            logger.info("验证码图片已保存为captcha.jpg")

            captcha = self.ocr.classification(response.content)
            logger.info(f"识别验证码: {captcha}")
            return captcha
        except Exception as e:
            logger.error(f"获取验证码异常: {str(e)}")
            raise e

    def login(self, username: str, password: str) -> bool:
        try:
            execution, pwd_salt = self._get_login_params()
            encrypted_pwd = encrypt_password(password, pwd_salt)
            captcha = ""
            if self.check_need_captcha(username):
                captcha = self._get_captcha()
            data = {
                "username": username,
                "password": encrypted_pwd,
                "execution": execution,
                "captcha": captcha,
                "_eventId": "submit",
                "cllt": "userNameLogin",
                "dllt": "generalLogin",
                "lt": "",
                "rememberMe": "true",
                "service": self.service_url,
            }

            response = self.session.post(LOGIN_URL, data=data)
            logger.info(f"登录响应状态码: {response.status_code}")

            if not response.ok:
                error_reason = self._get_html_error(response.text)
                logger.error(f"登录失败: {response.status_code}, 原因: {error_reason}")
                raise RuntimeError(
                    f"登录失败: {response.status_code}, 原因: {error_reason}"
                )

            return self.verify_session()

        except Exception as e:
            logger.error(f"登录流程异常: {str(e)}")
            raise

    def verify_session(self) -> bool:
        try:
            response = self.session.get(LOGIN_URL)
            if not response.ok:
                logger.error(f"会话验证失败: {response.status_code}")
                return False
            pwd_encrypt_salt_match = self._pwd_encrypt_salt_pattern.search(response.text)
            return pwd_encrypt_salt_match is not None

        except Exception as e:
            logger.error(f"会话验证异常: {str(e)}")
            raise

    def get_cookies(self) -> dict:
        return self.session.cookies.get_dict()

    def get_params(self) -> dict:
        self.login_params = LogParser.get_params_from_log_entries(
            LoggerFactory.get_root_logger_logs()
        )
        return self.login_params
