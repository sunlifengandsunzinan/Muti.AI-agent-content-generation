import requests
import re
import json

uid = "48881167027"

# Try 1: direct user page
url = f"https://www.douyin.com/user/{uid}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}
r = requests.get(url, headers=headers, timeout=10)
print("Status:", r.status_code)
print("URL:", r.url)

# check title
m = re.search(r"<title>(.*?)</title>", r.text, re.DOTALL)
print("Title:", m.group(1) if m else "N/A")

# check for RENDER_DATA
m2 = re.search(r'RENDER_DATA[^>]*>([^<]+)<', r.text)
if m2:
    from urllib.parse import unquote
    data = unquote(m2.group(1))
    # find user info patterns
    nick = re.search(r'"nickname":"([^"]+)"', data)
    desc = re.search(r'"desc":"([^"]+)"', data)
    follower = re.search(r'"followerCount":(\d+)', data)
    following = re.search(r'"followingCount":(\d+)', data)
    like = re.search(r'"totalFavorited":(\d+)', data)
    print("Nickname:", nick.group(1) if nick else "N/A")
    print("Desc:", desc.group(1)[:100] if desc else "N/A")
    print("Followers:", follower.group(1) if follower else "N/A")
    print("Following:", following.group(1) if following else "N/A")
    print("Total likes:", like.group(1) if like else "N/A")
else:
    print("No RENDER_DATA found")
    # Show part of page for debugging
    print("\n--- Page snippet ---")
    print(r.text[:2000])
