import sys
sys.path.insert(0, r'D:\MediaCrawler')

with open(r'D:\MediaCrawler\config\base_config.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Set cookie mode, disable CDP
content = content.replace('ENABLE_CDP_MODE = True', 'ENABLE_CDP_MODE = False')
content = content.replace('HEADLESS = False', 'HEADLESS = True')

# Update cookie
new_cookie = 'a1=19e69ad5bb9q7zw8k7pok7jyeya06x3a55ca5uhlc50000307356; webId=2779a142fcfcfc60c228994889c521cd; gid=yjdKj0fKf42yyjdKj0f2D27xDjAWuEYTWUlTS1SWVvdv00288KCq02888q8Wq2K84S8JSqJd; abRequestId=2779a142fcfcfc60c228994889c521cd; ets=1779889525696; x-rednote-datactry=CN; x-rednote-holderctry=CN; web_session=040069bb62b63f5a5050c32016384bd1d1df10; id_token=VjEAAMZ0v2u1NECQEmjaVbe86xt3WRj0rbAJ0Y2qz7Tv9BpLC139rWS56/tZr1K7zILmikWgzY0RaWzaKmobr8zmPIK7Ww/ALMQHuM4b/R+a2ICykosYyOCM2UDLKa4/zarBxwji; webBuild=6.15.2; acw_tc=0ad6222d17807591472364775e197aad11b85eb93d5273e4c817a99efa7b54; xsecappid=xhs-pc-web; unread={%22ub%22:%226a2213300000000022015319%22%2C%22ue%22:%226a1b748b000000000702c35e%22%2C%22uc%22:31}; websectiga=6169c1e84f393779a5f7de7303038f3b47a78e47be716e7bec57ccce17d45f99; sec_poison_id=c7df7266-2fe9-478c-90b8-6bf9a6749122; loadts=1780760419663'
import re
content = re.sub(r'COOKIES\s*=\s*"[^"]*"', f'COOKIES = "{new_cookie}"', content)

# Increase scrape limit to get enough content
content = content.replace('CRAWLER_MAX_NOTES_COUNT = 10', 'CRAWLER_MAX_NOTES_COUNT = 30')

with open(r'D:\MediaCrawler\config\base_config.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Config updated')
