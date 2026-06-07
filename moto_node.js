const https = require('https');
const http = require('http');
const { URL } = require('url');

function fetchUrl(url, cookie = '') {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const mod = parsed.protocol === 'https:' ? https : http;
    const opts = {
      hostname: parsed.hostname,
      port: parsed.port || 443,
      path: parsed.pathname + parsed.search,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Ch-Ua': '"Not-A.Brand";v="99", "Chromium";v="134"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Referer': 'https://www.58moto.com/'
      },
      timeout: 15000
    };
    const req = mod.get(opts, (res) => {
      let chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => {
        const buf = Buffer.concat(chunks);
        let data;
        try {
          data = buf.toString('utf-8');
        } catch {
          data = '<binary>';
        }
        resolve({ status: res.statusCode, headers: res.headers, data, raw: buf, url });
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
  });
}

// 58moto structure
const pages = [
  'https://www.58moto.com/',
  'https://www.58moto.com/portal.php',
  'https://www.58moto.com/forum.php',
  'https://www.58moto.com/forum-2-1.html',   // 摩托车论坛
  'https://www.58moto.com/forum-36-1.html',  // 摩旅天下
  'https://www.58moto.com/forum-46-1.html',  // 骑行装备
  'https://www.58moto.com/forum-47-1.html',  // 骑行路线
];

(async () => {
  for (const url of pages) {
    try {
      const r = await fetchUrl(url);
      console.log(`\n=== ${url} ===`);
      console.log(`Status: ${r.status}, Len: ${r.raw.length}`);
      
      if (r.data.includes('acw_tc') || r.data.includes('aliyun_waf')) {
        console.log('BLOCKED by WAF');
        continue;
      }
      
      // Extract useful info
      const titleMatch = r.data.match(/<title>([^<]+)<\/title>/i);
      if (titleMatch) console.log(`Title: ${titleMatch[1]}`);
      
      // Find all forum/thread links
      const links = r.data.match(/<a[^>]*href="([^"]*)"[^>]*>([^<]+)<\/a>/gi);
      if (links) {
        links.slice(0, 20).forEach(l => {
          const clean = l.replace(/<[^>]+>/g, ' ').trim();
          if (clean.length > 2 && !clean.includes('javascript') && !clean.includes('#')) {
            console.log(`  ${clean}`);
          }
        });
      }
    } catch(e) {
      console.log(`FAIL ${url}: ${e.message}`);
    }
  }
})();
