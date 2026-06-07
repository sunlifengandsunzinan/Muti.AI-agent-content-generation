const WebSocket = require('ws');
const fs = require('fs');

const CLIP = { x: 160, y: 72, width: 774, height: 447, scale: 1 };

const TASKS = [
  { id: 'CEE585C1A03C19F6D1AC9DDE070A5C00', dir: 'C:\\Users\\Administrator\\.openclaw\\workspace\\盛京铁骑_路线分析\\', 
    ts: [0, 11, 30, 48], 
    files: ['01_00-00_沈阳-辽阳-本溪摩旅环线.jpg','02_00-11_盛京铁骑摩友.jpg','03_00-30_路线导航.jpg','04_00-48_总结.jpg'] },
  { id: '3CE22687D93B813542F3ABADA46DF808', dir: 'C:\\Users\\Administrator\\.openclaw\\workspace\\盛京铁骑_大伙房水库\\',
    ts: [0, 15, 30, 45],
    files: ['01_00-00_大伙房水库骑行.jpg','02_00-15_温道大桥路段.jpg','03_00-30_路线沿途风景.jpg','04_00-45_骑行总结.jpg'] }
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
    }, 12000);
  });
}

async function execTask(task) {
  const ws = new WebSocket('ws://127.0.0.1:18800/devtools/page/' + task.id);
  ws.on('message', raw => {
    let msg;
    try { msg = JSON.parse(raw.toString()); } catch(e) { return; }
    if (msg.id && pending[msg.id]) {
      pending[msg.id].resolve(msg);
      delete pending[msg.id];
    }
  });
  
  await new Promise((r, e) => { ws.on('open', r); ws.on('error', e); });
  console.log('  Connected');
  
  for (let i = 0; i < task.ts.length; i++) {
    process.stdout.write(`  [${task.ts[i]}s] ${task.files[i]} ... `);
    try {
      await send(ws, 'Runtime.evaluate', {
        expression: 'document.querySelector(\'video\').currentTime=' + task.ts[i]
      });
      await new Promise(r => setTimeout(r, 1500));
      
      const res = await send(ws, 'Page.captureScreenshot', {
        format: 'jpeg', quality: 85, clip: CLIP
      });
      
      if (res.result && res.result.data) {
        const buf = Buffer.from(res.result.data, 'base64');
        fs.writeFileSync(task.dir + task.files[i], buf);
        console.log(`OK (${buf.length} bytes)`);
      } else {
        console.log('FAIL: ' + (res.error ? res.error.message : 'no data'));
      }
    } catch (e) {
      console.log('FAIL: ' + e.message);
    }
  }
  ws.close();
}

async function main() {
  console.log('=== Task 1: 辽阳本溪环线 (clipped to video) ===');
  await execTask(TASKS[0]);
  console.log('\\n=== Task 2: 大伙房水库 (clipped to video) ===');
  await execTask(TASKS[1]);
  console.log('\\nAll done! Video-only screenshots saved.');
}
main().catch(e => console.error('FATAL:', e));
