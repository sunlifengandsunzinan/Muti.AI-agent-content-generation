const WebSocket = require('ws');
const fs = require('fs');

const TARGET_ID = 'AE668D006D05180891DEBB1C3E9DBDC0';
const WS_URL = 'ws://127.0.0.1:18800/devtools/page/' + TARGET_ID;
const OUTPUT_DIR = 'C:\\Users\\Administrator\\.openclaw\\workspace\\盛京铁骑_路线分析\\';

const TIMESTAMPS = [
  { time: 0,   file: '01_00-00_沈阳-辽阳-本溪摩旅环线.jpg' },
  { time: 11,  file: '02_00-11_盛京铁骑摩友.jpg' },
  { time: 30,  file: '03_00-30_路线导航.jpg' },
  { time: 48,  file: '04_00-48_总结.jpg' }
];

let msgId = 0;
const pending = {};

function send(ws, method, params) {
  return new Promise((resolve, reject) => {
    const id = ++msgId;
    pending[id] = { resolve, reject };
    ws.send(JSON.stringify({ id, method, params }));
    setTimeout(() => {
      if (pending[id]) {
        delete pending[id];
        reject(new Error('timeout'));
      }
    }, 8000);
  });
}

async function main() {
  const ws = new WebSocket(WS_URL);
  
  ws.on('message', (raw) => {
    const msg = JSON.parse(raw.toString());
    if (msg.id && pending[msg.id]) {
      pending[msg.id].resolve(msg);
      delete pending[msg.id];
    }
  });

  await new Promise((resolve, reject) => {
    ws.on('open', resolve);
    ws.on('error', reject);
  });
  console.log('WebSocket connected!');

  for (const ts of TIMESTAMPS) {
    console.log(`[${ts.time}s] Capturing ${ts.file} ...`);
    
    // Set video time
    await send(ws, 'Runtime.evaluate', {
      expression: `document.querySelector('video').currentTime = ${ts.time}`,
      awaitPromise: false
    });
    
    // Wait for frame render
    await new Promise(r => setTimeout(r, 1200));
    
    // Capture screenshot
    const res = await send(ws, 'Page.captureScreenshot', {
      format: 'jpeg',
      quality: 80
    });
    
    if (res.result && res.result.data) {
      const buf = Buffer.from(res.result.data, 'base64');
      fs.writeFileSync(OUTPUT_DIR + ts.file, buf);
      console.log(`  OK: saved ${buf.length} bytes`);
    } else {
      console.log(`  FAIL: ${JSON.stringify(res.error || 'no data').substring(0, 200)}`);
    }
  }
  
  ws.close();
  console.log('\\nAll done! Screenshots in: ' + OUTPUT_DIR);
}

main().catch(e => console.error('ERROR:', e));
