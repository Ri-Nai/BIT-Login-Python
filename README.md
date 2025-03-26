# 🔑 BIT-Login-Python

北京理工大学统一身份认证登录工具

## ✨ 功能特性

- 支持北京理工大学统一身份认证系统登录
- 自动处理验证码识别
- 提供登录会话 Cookie 获取
- 支持配置文件方式设置登录信息

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🚀 使用方法

### 🔧 方式一：使用配置文件

1. 创建 `settings.json` 文件，配置以下信息：
```json
{
    "username": "你的学号",
    "password": "你的密码",
    "callback_url": "登录成功后的回调地址"
}
```
其中 `callback_url` 是登录成功后的回调地址，可以为空。    
例如填写 `https://ibit.yanhekt.cn/proxy/v1/cas/callback` 就可以获得 `ibit.yanhekt.cn` 的 Cookie。  
这个回调地址的获取可以在 `inprivate` 模式下，打开对应的网址，在登录界面的 `url` 中可以找到 `https://login.bit.edu.cn/authserver/login?service=callback_url` 这样的地址。

2. 运行程序：
```bash
python main.py
```

### ⌨️ 方式二：命令行交互

直接运行程序，按提示输入学号和密码：
```bash
python main.py
```
会自动保存登录信息到 `settings.json` 文件中。

### 📚 作为模块使用

```python
from login_service import LoginService

login_service = LoginService(callback_url="你的回调地址")
login_service.login(username="你的学号", password="你的密码")
cookies = login_service.get_cookies()
```

## ⚠️ 注意事项

- 请妥善保管你的账号密码信息
- 验证码图片会临时保存在 `output/captcha.jpg` 文件中
- 登录参数会临时保存在 `output/params.json` 文件中
- 登录会话 Cookie 会临时保存在 `output/cookies.json` 文件中

## 📌 依赖项

- `requests`
- `beautifulsoup4`
- `ddddocr`
- `pycryptodome`

## 📜 许可证

[WTFPL](LICENSE)

## 🙏 致谢

- [BITLogin-Node](https://github.com/BIT-BOBH/BITLogin-Node)
- [BIT101-Android](https://github.com/BIT101-Dev/BIT101-Android)
- [BIT101-GO](https://github.com/BIT101-Dev/BIT101-GO)

## ☕ Kotlin 版本

[iBitChatKotlin](https://github.com/Ri-Nai/iBitChatKotlin/) 中 `LoginService` / `LoginApi` 等模块的实现，可以参考。

由于 `Kotlin` 用的人不多，所以就不单独开一个项目了。
