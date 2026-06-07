import sys
sys.path.insert(0, r'D:\MediaCrawler')

with open(r'D:\MediaCrawler\config\base_config.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Switch to CDP mode - connect to existing Chrome
content = content.replace('ENABLE_CDP_MODE = False', 'ENABLE_CDP_MODE = True')
content = content.replace('CDP_CONNECT_EXISTING = False', 'CDP_CONNECT_EXISTING = True')
content = content.replace('CRAWLER_TYPE = (\n    "search"', 'CRAWLER_TYPE = (\n    "search"')
content = content.replace('HEADLESS = True', 'HEADLESS = False')

# Ensure login is cookie based but use CDP for browser control
content = content.replace('LOGIN_TYPE = "cookie"', 'LOGIN_TYPE = "qrcode"')

with open(r'D:\MediaCrawler\config\base_config.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('CDP mode enabled - connect to existing Chrome')
