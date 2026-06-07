# Mac task: 采集摩托范 (moto.yiche.com) 摩旅路书帖子
# 通过 Mac 的浏览器 node 能力

export PATH=/usr/local/bin:$PATH

# 先看看摩托范的结构
openclaw node run --host 192.168.0.112 --port 18789 --display-name sunlifeng-Mac --node-id moto-scraper &
NODE_PID=$!
sleep 5

# 用 curl 先探一下摩托范的路书/帖子板块
curl -s -L "https://moto.yiche.com/route/" -o /tmp/moto_route.html 2>/dev/null
curl -s -L "https://moto.yiche.com/news/" -o /tmp/moto_news.html 2>/dev/null

echo "Done fetching"
kill $NODE_PID 2>/dev/null
