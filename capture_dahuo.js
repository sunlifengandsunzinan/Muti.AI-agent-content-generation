const WebSocket = require('ws');
const fs = require('fs');
const TARGET_ID = '464588F1D290B34E62B7B4CB994AEE5F';
const WS_URL = 'ws://127.0.0.1:18800/devtools/page/' + TARGET_ID;
const OUTPUT_DIR = 'C:\\Users\\Administrator\\.openclaw\\workspace\\盛京铁骑_大伙房水库\\';

const TIMESTAMPS = [
  { time: 0,   file: '01_00-00_大伙房水库骑行.jpg' },
  { time: 15,  file: '02_00-15_温道大桥路段.jpg' },
  { time: 30,  file: '03_00-30_路线沿途风景.jpg' },
  { time: 45,  file: '04_00-45_骑行总结.jpg' }
];

let msgId = 0;
const pending = {};

function send(ws, method, params) {
  return new Promise((resolve, reject) => {
    const id = ++msgId;
    pending[id] = { resolve, reject };
    ws.send(JSON.stringify({ id, method, params }));
    setTimeout(() => {
      if (pending[id]) { delete pending[id]; reject(new Error('timeout')); }
    }, 10000);
  });
}

async function main() {
  const ws = new WebSocket(WS_URL);
  ws.on('message', raw => {
    const msg = JSON.parse(raw.toString());
    if (msg.id && pending[msg.id]) {
      pending[msg.id].resolve(msg);
      delete pending[msg.id];
    }
  });
  await new Promise((r, e) => { ws.on('open', r); ws.on('error', e); });
  console.log('Connected!');

  for (const ts of TIMESTAMPS) {
    console.log(`[${ts.time}s] ${ts.file} ...`);
    await send(ws, 'Runtime.evaluate', {
      expression: `document.querySelector('video').currentTime = ${ts.time}`
    });
    await new Promise(r => setTimeout(r, 1000));
    const res = await send(ws, 'Page.captureScreenshot', { format: 'jpeg', quality: 80 });
    if (res.result && res.result.data) {
      const buf = Buffer.from(res.result.data, 'base64');
      fs.writeFileSync(OUTPUT_DIR + ts.file, buf);
      console.log(`  OK: ${buf.length} bytes`);
    } else {
      console.log(`  FAIL: ${JSON.stringify(res.error || 'no data').substring(0,150)}`);
    }
  }
  
  ws.close();
  console.log('\\nAll done! Saved to ' + OUTPUT_DIR);
}
main().catch(e => { console.error('ERROR:', e); process.exit(1); });
