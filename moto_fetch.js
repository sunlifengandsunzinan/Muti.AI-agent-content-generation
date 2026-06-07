const https = require('https');
const http = require('http');
const { URL } = require('url');

const KEYWORDS = ['摩旅路线', '摩托车路书', '骑行路线推荐', '摩旅'];

async function fetch(urlStr) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlStr);
    const mod = url.protocol === 'https:' ? https : http;
    const req = mod.get(urlStr, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/json,*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
      },
      timeout: 15000
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, data, url: urlStr }));
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
  });
}

// 搜索摩托范路书列表API
const routeUrls = [
  'https://moto.yiche.com/route/',  // 路书首页
  'https://moto-api.yiche.com/route/api/v1/route/list?pageNo=1&pageSize=10',
  'https://moto-api.yiche.com/route/api/v1/route/search?keyword=' + encodeURIComponent('摩旅'),
];

(async () => {
  for (const kw of KEYWORDS) {
    const url = `https://moto-api.yiche.com/route/api/v1/route/search?keyword=${encodeURIComponent(kw)}&pageNo=1&pageSize=10`;
    try {
      const result = await fetch(url);
      console.log(`\n=== ${kw} ===`);
      console.log(`Status: ${result.status}, Length: ${result.data.length}`);
      // Try to parse as JSON
      try {
        const json = JSON.parse(result.data);
        console.log(JSON.stringify(json, null, 2).slice(0, 2000));
      } catch {
        console.log(result.data.slice(0, 1000));
      }
    } catch (e) {
      console.log(`FAIL ${kw}: ${e.message}`);
    }
  }

  // Try route list API
  for (const url of routeUrls) {
    try {
      const result = await fetch(url);
      console.log(`\n=== ${url} ===`);
      console.log(`Status: ${result.status}, Length: ${result.data.length}`);
      try {
        const json = JSON.parse(result.data);
        console.log(JSON.stringify(json, null, 2).slice(0, 2000));
      } catch {
        // Look for route data in HTML
        const match = result.data.match(/routeList\s*[:=]\s*(\[[^\]]+\])/);
        if (match) console.log('MATCH:', match[1].slice(0, 2000));
        else console.log(result.data.slice(0, 500));
      }
    } catch (e) {
      console.log(`FAIL: ${e.message}`);
    }
  }
})();
