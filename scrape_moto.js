const https = require('https');
const http = require('http');

async function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? https : http;
    const req = mod.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': ''
      },
      timeout: 15000
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, data: data.slice(0, 5000), url }));
    });
    req.on('error', reject);
  });
}

async function main() {
  const urls = [
    'https://www.58moto.com/',
    'https://www.58moto.com/bbs/',
    'https://www.58moto.com/forum.php',
    'https://www.58moto.com/forum-2-1.html',
  ];
  
  for (const url of urls) {
    try {
      const result = await fetchUrl(url);
      console.log(`\n=== ${url} ===`);
      console.log(`Status: ${result.status}, Len: ${result.data.length}`);
      // Look for board/forum navigation
      const matches = result.data.match(/href="([^"]*(?:bbs|forum|route|thread|guide|travel)[^"]*)"/gi);
      if (matches) {
        matches.slice(0, 20).forEach(m => console.log(`  LINK: ${m}`));
      }
    } catch(e) {
      console.log(`FAIL ${url}: ${e.message}`);
    }
  }
}
main();
