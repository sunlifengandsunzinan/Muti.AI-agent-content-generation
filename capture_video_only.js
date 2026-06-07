const WebSocket = require('ws');
const fs = require('fs');

let msgId = 0;
const pending = {};

function send(ws, method, params) {
  return new Promise((resolve, reject) => {
    const id = ++msgId;
    pending[id] = { resolve, reject };
    ws.send(JSON.stringify({ id, method, params }));
    setTimeout(() => {
      if (pending[id]) { delete pending[id]; reject(new Error('timeout')); }
    }, 15000);
  });
}

async function captureTab(wsUrl, targetDir, timestamps) {
  const ws = new WebSocket(wsUrl);
  ws.on('message', raw => {
    let msg;
    try { msg = JSON.parse(raw.toString()); } catch (e) { return; }
    if (msg.id && pending[msg.id]) {
      pending[msg.id].resolve(msg);
      delete pending[msg.id];
    }
  });
  
  await new Promise((resolve, reject) => {
    ws.on('open', resolve);
    ws.on('error', reject);
  });
  console.log('  Connected');
  
  // First get the video rect
  const rectRes = await send(ws, 'Runtime.evaluate', {
    expression: '(function(){var v=document.querySelector(\'video\');if(!v){return \'\'};var r=v.getBoundingClientRect();return Math.round(r.x)+\',\'+Math.round(r.y)+\',\'+Math.round(r.width)+\',\'+Math.round(r.height)})()',
    awaitPromise: false
  });
  const rectStr = rectRes.result && rectRes.result.value;
  if (!rectStr) { console.log('  FAIL: no video rect'); ws.close(); return; }
  const [x, y, w, h] = rectStr.split(',').map(Number);
  console.log('  Video rect:', x, y, w, h);
  
  for (const ts of timestamps) {
    process.stdout.write(`  [${ts.time}s] ${ts.file} ... `);
    try {
      // Set time
      await send(ws, 'Runtime.evaluate', {
        expression: 'document.querySelector(\'video\').currentTime=' + ts.time,
        awaitPromise: false
      });
      await new Promise(r => setTimeout(r, 1200));
      
      // Capture clipped screenshot
      const r = await send(ws, 'Page.captureScreenshot', {
        format: 'jpeg',
        quality: 90,
        clip: { x, y, width: w, height: h, scale: 1 }
      });
      
      if (r.result && r.result.data) {
        const buf = Buffer.from(r.result.data, 'base64');
        fs.writeFileSync(targetDir + ts.file, buf);
        console.log(`OK (${buf.length} bytes)`);
      } else {
        console.log('FAIL: no data');
      }
    } catch (e) {
      console.log(`FAIL: ${e.message}`);
    }
  }
  
  ws.close();
}

async function main() {
  const http = require('http');
  const jsonData = await new Promise((resolve, reject) => {
    http.get('http://127.0.0.1:18800/json', res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve(JSON.parse(d)));
    });
  });
  
  const tab1 = jsonData.find(t => t.url.includes('7639753707559588763'));
  const tab2 = jsonData.find(t => t.url.includes('7638103676385654643'));
  if (!tab1 || !tab2) { console.log('ERROR: tabs not found'); return; }
  
  const BASE = 'ws://127.0.0.1:18800/devtools/page/';
  const DIR1 = 'C:\\Users\\Administrator\\.openclaw\\workspace\\盛京铁骑_路线分析\\';
  const DIR2 = 'C:\\Users\\Administrator\\.openclaw\\workspace\\盛京铁骑_大伙房水库\\';
  
  const TS1 = [
    { time: 0,  file: '01_00-00_沈阳-辽阳-本溪摩旅环线.jpg' },
    { time: 11, file: '02_00-11_盛京铁骑摩友.jpg' },
    { time: 30, file: '03_00-30_路线导航.jpg' },
    { time: 48, file: '04_00-48_总结.jpg' }
  ];
  const TS2 = [
    { time: 0,  file: '01_00-00_大伙房水库骑行.jpg' },
    { time: 15, file: '02_00-15_温道大桥路段.jpg' },
    { time: 30, file: '03_00-30_路线沿途风景.jpg' },
    { time: 45, file: '04_00-45_骑行总结.jpg' }
  ];
  
  console.log('=== Task 1: 辽阳本溪环线 ===');
  await captureTab(BASE + tab1.id, DIR1, TS1);
  
  console.log('\\n=== Task 2: 大伙房水库 ===');
  await captureTab(BASE + tab2.id, DIR2, TS2);
  
  console.log('\\nAll done! 8 clipped screenshots saved.');
}
main().catch(e => console.error('FATAL:', e));
