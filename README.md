# BIT-Login-Python

北京理工大学统一身份认证登录工具

## 功能特性

- 支持北京理工大学统一身份认证系统登录
- 自动处理验证码识别
- 支持密码加密
- 提供登录会话 Cookie 获取
- 支持配置文件方式设置登录信息

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式一：使用配置文件

1. 创建 `settings.json` 文件，配置以下信息：
```json
{
    "username": "你的学号",
    "password": "你的密码",
    "callback_url": "登录成功后的回调地址"
}
```
其中 `callback_url` 是登录成功后的回调地址，可以为空。例如填写 `https://ibit.yanhekt.cn/proxy/v1/cas/callback` 就可以获得 `ibit.yanhekt.cn` 的 Cookie。

2. 运行程序：
```bash
python main.py
```

### 方式二：命令行交互

直接运行程序，按提示输入学号和密码：
```bash
python main.py
```
会自动保存登录信息到 `settings.json` 文件中。

### 作为模块使用

```python
from login_service import LoginService

login_service = LoginService(callback_url="你的回调地址")
login_service.login(username="你的学号", password="你的密码")
cookies = login_service.get_cookies()
```

## 注意事项

- 请妥善保管你的账号密码信息
- 验证码图片会临时保存在 `captcha.jpg` 文件中

## 依赖项

- `requests`
- `beautifulsoup4`
- `ddddocr`
- `pycryptodome`

## 许可证

[WTFPL](LICENSE)
