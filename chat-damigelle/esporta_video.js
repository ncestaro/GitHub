const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const OUT = __dirname;
const WAV = require('path').join(require('os').tmpdir(), 'chat_audio.wav');
const FPS = 30;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 405, height: 720 }, deviceScaleFactor: 1080 / 405 });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(`file://${OUT}/chat_animata.html?record`);
  await p.waitForFunction(() => window.CHAT && window.CHAT.ready);
  const total = await p.evaluate(() => CHAT.total);
  const wav = await p.evaluate(() => CHAT.renderAudioWav());
  fs.writeFileSync(WAV, Buffer.from(wav, 'base64'));
  const n = Math.ceil(total * FPS);
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', WAV, '-vf', 'scale=1080:1920:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
    '-af', 'volume=8dB', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', `${OUT}/chat_damigelle.mp4`], { stdio: ['pipe', 'ignore', 'inherit'] });
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => CHAT.renderAt(t), i / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`frame ${i}/${n}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
  console.log('done', total);
})();
