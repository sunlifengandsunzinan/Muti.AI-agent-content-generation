# 写出 good 的文件
# 从 ln_filtered_199.json 找到 331/丹东 相关的原始标题
import json
with open(r'D:\摩旅数据采集目录\ln_filtered_199.json', encoding='utf-8-sig') as f:
    data = json.load(f)
for r in data:
    title = r.get('title', '')
    if any(kw in title for kw in ['331','丹东','集安','边境']):
        print(f'{title[:100]}')
