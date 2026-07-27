const https = require('https');

const uid = '48881167027';
const url = `/user/${uid}`;
const options = {
  hostname: 'www.douyin.com',
  path: url,
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
  }
};

https.get(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    console.log('Status:', res.statusCode);
    // find title
    const titleMatch = data.match(/<title>([^<]+)<\/title>/);
    console.log('Title:', titleMatch ? titleMatch[1] : 'N/A');
    // find RENDER_DATA
    const renderMatch = data.match(/RENDER_DATA[^>]*>([^<]+)<\/script>/);
    if (renderMatch) {
      const decoded = decodeURIComponent(renderMatch[1]);
      // find user info
      const nickMatch = decoded.match(/"nickname":"([^"]+)"/);
      const descMatch = decoded.match(/"desc":"([^"]+)"/);
      const folMatch = decoded.match(/"followerCount":(\d+)/);
      const fgMatch = decoded.match(/"followingCount":(\d+)/);
      const likeMatch = decoded.match(/"totalFavorited":(\d+)/);
      const sigMatch = decoded.match(/"signature":"([^"]+)"/);
      console.log('Nickname:', nickMatch ? nickMatch[1] : 'N/A');
      console.log('Desc:', descMatch ? descMatch[1] : 'N/A');
      console.log('Followers:', folMatch ? folMatch[1] : 'N/A');
      console.log('Following:', fgMatch ? fgMatch[1] : 'N/A');
      console.log('Total likes:', likeMatch ? likeMatch[1] : 'N/A');
      console.log('Signature:', sigMatch ? sigMatch[1] : 'N/A');
    } else {
      console.log('No RENDER_DATA found');
      // First 1500 chars of body
      const bodyStart = data.indexOf('<body') >= 0 ? data.substring(data.indexOf('<body'), data.indexOf('<body') + 1500) : data.substring(0, 1500);
      console.log('Body start:', bodyStart.substring(0, 1000));
    }
  });
}).on('error', e => console.log('Error:', e.message));
