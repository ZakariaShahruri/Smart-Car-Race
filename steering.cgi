#!/bin/bash
echo "Content-type: text/html"
echo ""

cat <<'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>RC Race Control</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Barlow+Condensed:wght@300;400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --red:      #ff1e1e;
      --red-dark: #6b0808;
      --amber:    #ffaa00;
      --green:    #00e676;
      --white:    #ffffff;
      --off-white:#c8c4bc;
      --muted:    #6b6760;
      --bg:       #0a0908;
      --card:     #1c1a18;
      --border:   #2a2724;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      height: 100%; background: var(--bg); color: var(--white);
      font-family: 'Barlow Condensed', sans-serif;
      overscroll-behavior: none; user-select: none;
    }
    body {
      display: flex; flex-direction: column; align-items: center;
      justify-content: flex-start; min-height: 100vh; padding: 16px;
      background-image: radial-gradient(ellipse 80% 40% at 50% -10%, rgba(200,10,10,.15) 0%, transparent 70%);
    }
    .panel { width: 100%; max-width: 480px; display: flex; flex-direction: column; gap: 16px; }

    /* HEADER */
    .header { text-align: center; padding-bottom: 12px; border-bottom: 1px solid; border-image: linear-gradient(90deg,transparent,var(--red),transparent) 1; }
    .eyebrow { font-size: .6rem; letter-spacing: .25em; color: var(--red); text-transform: uppercase; margin-bottom: 4px; }
    .title { font-family: 'Orbitron', monospace; font-weight: 900; font-size: clamp(1.4rem,6vw,2rem); letter-spacing: .06em;
      background: linear-gradient(180deg,#fff 0%,#bbb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .title em { background: linear-gradient(180deg,#ff6060 0%,var(--red) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-style: normal; }

    /* TELEMETRY */
    .tele { display: grid; grid-template-columns: repeat(3,1fr); gap: 8px; }
    .tele-cell { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 8px; text-align: center; position: relative; overflow: hidden; transition: border-color .2s; }
    .tele-cell::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background: var(--muted); transition: background .2s; }
    .tele-cell.active::before { background: var(--red); box-shadow: 0 0 8px var(--red); }
    .tele-cell.active { border-color: var(--red-dark); }
    .tele-label { font-size: .55rem; letter-spacing: .15em; color: var(--muted); text-transform: uppercase; margin-bottom: 4px; }
    .tele-value { font-family: 'Orbitron', monospace; font-weight: 700; font-size: .8rem; color: var(--off-white); transition: color .2s; }
    .tele-cell.active .tele-value { color: var(--red); }

    /* DPAD */
    .dpad-wrap { display: flex; flex-direction: column; align-items: center; gap: 12px; }
    .dpad {
      display: grid;
      grid-template-columns: 1fr 1.1fr 1fr;
      grid-template-rows: auto auto auto;
      gap: 8px; width: 100%; max-width: 340px;
    }
    .btn {
      display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
      padding: 18px 10px; border-radius: 10px; background: var(--card); border: 1px solid var(--border);
      color: var(--off-white); font-family: 'Orbitron', monospace; font-size: .55rem; font-weight: 700;
      letter-spacing: .1em; text-transform: uppercase; cursor: pointer; transition: all .1s ease;
      -webkit-tap-highlight-color: transparent; touch-action: none;
    }
    .btn:hover { border-color: var(--red); box-shadow: 0 0 0 1px var(--red-dark), 0 4px 20px rgba(255,30,30,.2); color: var(--white); }
    .btn.pressed { background: #2a0808; border-color: var(--red); box-shadow: 0 0 0 1px var(--red), 0 0 20px rgba(255,30,30,.3); color: var(--red); transform: scale(.96); }
    .btn-icon { font-size: 1.3rem; line-height: 1; }
    .btn-fwd  { grid-column:2; grid-row:1; border-top: 2px solid #cc1010; }
    .btn-fl   { grid-column:1; grid-row:1; }
    .btn-fr   { grid-column:3; grid-row:1; }
    .btn-left { grid-column:1; grid-row:2; border-left: 2px solid #cc1010; }
    .btn-right{ grid-column:3; grid-row:2; border-right: 2px solid #cc1010; }
    .btn-bl   { grid-column:1; grid-row:3; }
    .btn-br   { grid-column:3; grid-row:3; }
    .btn-bwd  { grid-column:2; grid-row:3; border-bottom: 2px solid #cc1010; }
    .btn-stop {
      grid-column:2; grid-row:2;
      background: #1a0505; border: 1px solid var(--red-dark); border-radius: 50%;
      width: 78px; height: 78px; justify-self: center; align-self: center; padding: 0; color: var(--red);
    }
    .btn-stop:hover { background: #260808; box-shadow: 0 0 0 1px var(--red), 0 0 30px rgba(255,30,30,.4); }
    .btn-stop .btn-icon { font-size: 1.6rem; }

    /* JOYSTICK */
    .joystick-wrap { display: flex; flex-direction: column; align-items: center; gap: 8px; }
    .joystick-label { font-size: .6rem; letter-spacing: .2em; color: var(--muted); text-transform: uppercase; }
    .joystick-ring {
      width: 180px; height: 180px; border-radius: 50%;
      background: var(--card); border: 2px solid var(--border);
      position: relative; touch-action: none; cursor: grab;
      box-shadow: inset 0 0 30px rgba(0,0,0,.5);
    }
    .joystick-ring::before {
      content:''; position:absolute; inset:20px; border-radius:50%;
      border: 1px dashed var(--border);
    }
    .joystick-knob {
      width: 60px; height: 60px; border-radius: 50%;
      background: radial-gradient(circle at 35% 35%, #444, #1a1a1a);
      border: 2px solid var(--red); position: absolute;
      top: 50%; left: 50%; transform: translate(-50%,-50%);
      transition: box-shadow .1s;
      box-shadow: 0 0 10px rgba(255,30,30,.3);
      pointer-events: none;
    }
    .joystick-ring.active .joystick-knob { box-shadow: 0 0 20px rgba(255,30,30,.6); }

    /* SPEED SLIDER */
    .speed-wrap { display: flex; flex-direction: column; gap: 6px; }
    .speed-header { display: flex; justify-content: space-between; align-items: center; }
    .speed-label { font-size: .6rem; letter-spacing: .2em; color: var(--muted); text-transform: uppercase; }
    .speed-val { font-family: 'Orbitron', monospace; font-size: .75rem; color: var(--red); font-weight: 700; }
    input[type=range] {
      width: 100%; -webkit-appearance: none; appearance: none;
      height: 6px; border-radius: 3px; outline: none; cursor: pointer;
      background: linear-gradient(to right, var(--red) 0%, var(--red) var(--pct), var(--border) var(--pct), var(--border) 100%);
    }
    input[type=range]::-webkit-slider-thumb {
      -webkit-appearance: none; width: 20px; height: 20px; border-radius: 50%;
      background: var(--white); border: 2px solid var(--red);
      box-shadow: 0 0 8px rgba(255,30,30,.4);
    }

    /* AUX */
    .aux { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .btn-aux {
      display: flex; align-items: center; justify-content: center; gap: 8px;
      padding: 12px; border-radius: 8px; background: var(--card); border: 1px solid var(--border);
      color: var(--off-white); font-family: 'Orbitron', monospace; font-size: .55rem;
      font-weight: 600; letter-spacing: .1em; text-transform: uppercase; cursor: pointer;
      transition: all .12s ease; -webkit-tap-highlight-color: transparent;
    }
    .btn-aux:hover { border-color: var(--amber); color: var(--amber); box-shadow: 0 0 10px rgba(255,170,0,.2); }
    .btn-aux .ic { font-size: 1rem; }

    /* KEYBOARD HINT */
    .kbd-hint { text-align: center; font-size: .6rem; letter-spacing: .15em; color: var(--muted); text-transform: uppercase; }
    .key { display: inline-block; background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 1px 5px; font-family: monospace; }

    /* TAB SWITCHER */
    .tabs { display: flex; gap: 4px; background: var(--card); border-radius: 8px; padding: 4px; }
    .tab { flex: 1; padding: 8px; border-radius: 6px; text-align: center; cursor: pointer;
      font-family: 'Orbitron', monospace; font-size: .6rem; letter-spacing: .1em;
      color: var(--muted); transition: all .15s; border: none; background: none; }
    .tab.active { background: var(--red-dark); color: var(--white); box-shadow: 0 0 10px rgba(255,30,30,.3); }

    .control-panel { display: none; flex-direction: column; align-items: center; gap: 12px; }
    .control-panel.visible { display: flex; }

    .footer { text-align: center; font-size: .55rem; letter-spacing: .2em; color: var(--muted); text-transform: uppercase; padding-top: 4px; }
    .pip { display:inline-block; width:4px; height:4px; background:var(--red); border-radius:50%; margin:0 6px; vertical-align:middle; animation: blink 1.2s step-start infinite; }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }
  </style>
</head>
<body>
<div class="panel">

  <header class="header">
    <div class="eyebrow">PIT LANE CONTROL</div>
    <div class="title">RC <em>RACE</em> CTRL</div>
  </header>

  <div class="tele">
    <div class="tele-cell" id="tele-dir">
      <div class="tele-label">Moving</div>
      <div class="tele-value" id="tele-dir-val">STOPPED</div>
    </div>
    <div class="tele-cell" id="tele-steer">
      <div class="tele-label">Steering</div>
      <div class="tele-value" id="tele-steer-val">STRAIGHT</div>
    </div>
    <div class="tele-cell" id="tele-speed">
      <div class="tele-label">Speed</div>
      <div class="tele-value" id="tele-speed-val">100%</div>
    </div>
  </div>

  <!-- TAB SWITCHER -->
  <div class="tabs">
    <button class="tab active" onclick="switchTab('dpad')">D-PAD</button>
    <button class="tab" onclick="switchTab('joystick')">JOYSTICK</button>
  </div>

  <!-- DPAD PANEL -->
  <div class="control-panel visible" id="panel-dpad">
    <div class="dpad">
      <button class="btn btn-fl"   data-cmd="forward-left"  onpointerdown="startCmd(this)" onpointerup="stopCmd()" onpointerleave="stopCmd()">
        <span class="btn-icon">↖</span><span>FL</span>
      </button>
      <button class="btn btn-fwd"  data-cmd="forward"       onpointerdown="startCmd(this)" onpointerup="stopCmd()" onpointerleave="stopCmd()">
        <span class="btn-icon">▲</span><span>FWD</span>
      </button>
      <button class="btn btn-fr"   data-cmd="forward-right" onpointerdown="startCmd(this)" onpointerup="stopCmd()" onpointerleave="stopCmd()">
        <span class="btn-icon">↗</span><span>FR</span>
      </button>

      <button class="btn btn-left" data-cmd="left"          onpointerdown="startCmd(this)" onpointerup="stopCmd()" onpointerleave="stopCmd()">
        <span class="btn-icon">◀</span><span>LEFT</span>
      </button>
      <button class="btn btn-stop" onclick="sendCmd('stop')">
        <span class="btn-icon">⏹</span>
      </button>
      <button class="btn btn-right" data-cmd="right"        onpointerdown="startCmd(this)" onpointerup="stopCmd()" onpointerleave="stopCmd()">
        <span class="btn-icon">▶</span><span>RIGHT</span>
      </button>

      <button class="btn btn-bl"   data-cmd="backward-left" onpointerdown="startCmd(this)" onpointerup="stopCmd()" onpointerleave="stopCmd()">
        <span class="btn-icon">↙</span><span>BL</span>
      </button>
      <button class="btn btn-bwd"  data-cmd="backward"      onpointerdown="startCmd(this)" onpointerup="stopCmd()" onpointerleave="stopCmd()">
        <span class="btn-icon">▼</span><span>REV</span>
      </button>
      <button class="btn btn-br"   data-cmd="backward-right" onpointerdown="startCmd(this)" onpointerup="stopCmd()" onpointerleave="stopCmd()">
        <span class="btn-icon">↘</span><span>BR</span>
      </button>
    </div>
    <div class="kbd-hint">
      Keyboard: <span class="key">↑</span><span class="key">↓</span><span class="key">←</span><span class="key">→</span> to drive &nbsp;|&nbsp; <span class="key">Space</span> to stop
    </div>
  </div>

  <!-- JOYSTICK PANEL -->
  <div class="control-panel" id="panel-joystick">
    <div class="joystick-wrap">
      <div class="joystick-label">Touch &amp; Drag to Steer</div>
      <div class="joystick-ring" id="joystick">
        <div class="joystick-knob" id="knob"></div>
      </div>
    </div>
  </div>

  <!-- SPEED -->
  <div class="speed-wrap">
    <div class="speed-header">
      <span class="speed-label">Speed</span>
      <span class="speed-val" id="speed-display">100%</span>
    </div>
    <input type="range" id="speed-slider" min="20" max="100" value="100"
      style="--pct:100%"
      oninput="updateSpeed(this.value)">
  </div>

  <!-- AUX -->
  <div class="aux">
    <button class="btn-aux" onclick="sendCmd('spin-left')"><span class="ic">↺</span> SPIN L</button>
    <button class="btn-aux" onclick="sendCmd('spin-right')"><span class="ic">↻</span> SPIN R</button>
  </div>

  <div class="footer">Poor Man's Steering Wheel <span class="pip"></span> v4.0</div>
</div>

<script>
  let currentCmd = null;
  let sendInterval = null;
  let speed = 100;
  let lastSent = null;

  function updateSpeed(val) {
    speed = parseInt(val);
    document.getElementById('speed-display').textContent = speed + '%';
    document.getElementById('tele-speed-val').textContent = speed + '%';
    document.querySelector('input[type=range]').style.setProperty('--pct', speed + '%');
  }

  function sendCmd(cmd) {
    if (cmd === lastSent && cmd !== 'stop') return;
    lastSent = cmd;

    const url = `/cgi-bin/car_control.cgi/${cmd}`;
    fetch(url).catch(() => {});

    // Update telemetry
    const dirMap = { forward:'FORWARD', backward:'REVERSE', stop:'STOPPED',
      'forward-left':'FORWARD','forward-right':'FORWARD',
      'backward-left':'REVERSE','backward-right':'REVERSE',
      'spin-left':'SPINNING','spin-right':'SPINNING', left:'FORWARD', right:'FORWARD' };
    const steerMap = { forward:'STRAIGHT', backward:'STRAIGHT', stop:'STRAIGHT',
      left:'LEFT', right:'RIGHT', 'forward-left':'LEFT','forward-right':'RIGHT',
      'backward-left':'LEFT','backward-right':'RIGHT',
      'spin-left':'LEFT','spin-right':'RIGHT' };

    const dirEl = document.getElementById('tele-dir');
    const steerEl = document.getElementById('tele-steer');
    const dirVal = document.getElementById('tele-dir-val');
    const steerVal = document.getElementById('tele-steer-val');

    dirVal.textContent = dirMap[cmd] || 'STOPPED';
    steerVal.textContent = steerMap[cmd] || 'STRAIGHT';

    dirEl.classList.toggle('active', cmd !== 'stop');
    steerEl.classList.toggle('active', steerMap[cmd] !== 'STRAIGHT' && cmd !== 'stop');
  }

  function startCmd(btn) {
    const cmd = btn.dataset.cmd;
    document.querySelectorAll('.btn').forEach(b => b.classList.remove('pressed'));
    btn.classList.add('pressed');
    currentCmd = cmd;
    sendCmd(cmd);
    clearInterval(sendInterval);
    sendInterval = setInterval(() => { if (currentCmd) { lastSent = null; sendCmd(currentCmd); } }, 200);
  }

  function stopCmd() {
    clearInterval(sendInterval);
    sendInterval = null;
    currentCmd = null;
    lastSent = null;
    document.querySelectorAll('.btn').forEach(b => b.classList.remove('pressed'));
    sendCmd('stop');
  }

  // Keyboard control
  const keyMap = {
    ArrowUp: 'forward', ArrowDown: 'backward',
    ArrowLeft: 'left', ArrowRight: 'right', ' ': 'stop'
  };
  const keysDown = new Set();

  function getKeyCmd() {
    const fwd = keysDown.has('ArrowUp');
    const bwd = keysDown.has('ArrowDown');
    const lft = keysDown.has('ArrowLeft');
    const rgt = keysDown.has('ArrowRight');
    if (fwd && lft) return 'forward-left';
    if (fwd && rgt) return 'forward-right';
    if (bwd && lft) return 'backward-left';
    if (bwd && rgt) return 'backward-right';
    if (fwd) return 'forward';
    if (bwd) return 'backward';
    if (lft) return 'left';
    if (rgt) return 'right';
    return 'stop';
  }

  document.addEventListener('keydown', e => {
    if (!(e.key in keyMap) && e.key !== ' ') return;
    e.preventDefault();
    keysDown.add(e.key);
    const cmd = getKeyCmd();
    if (cmd !== currentCmd) { currentCmd = cmd; lastSent = null; sendCmd(cmd); }
  });

  document.addEventListener('keyup', e => {
    keysDown.delete(e.key);
    const cmd = getKeyCmd();
    currentCmd = cmd; lastSent = null; sendCmd(cmd);
  });

  // Joystick
  const joystick = document.getElementById('joystick');
  const knob = document.getElementById('knob');
  let joystickActive = false;
  let joystickOrigin = { x: 0, y: 0 };
  const DEAD = 0.15;
  const RADIUS = 60;

  function joystickCmd(nx, ny) {
    const ax = Math.abs(nx), ay = Math.abs(ny);
    if (ax < DEAD && ay < DEAD) return 'stop';
    const fwd = ny < -DEAD, bwd = ny > DEAD;
    const lft = nx < -DEAD, rgt = nx > DEAD;
    if (fwd && lft) return 'forward-left';
    if (fwd && rgt) return 'forward-right';
    if (bwd && lft) return 'backward-left';
    if (bwd && rgt) return 'backward-right';
    if (fwd) return 'forward';
    if (bwd) return 'backward';
    if (lft) return 'left';
    if (rgt) return 'right';
    return 'stop';
  }

  function moveKnob(clientX, clientY) {
    const rect = joystick.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    let dx = clientX - cx, dy = clientY - cy;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist > RADIUS) { dx = dx/dist*RADIUS; dy = dy/dist*RADIUS; }
    knob.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
    const nx = dx / RADIUS, ny = dy / RADIUS;
    const cmd = joystickCmd(nx, ny);
    if (cmd !== lastSent) { lastSent = null; sendCmd(cmd); }
  }

  joystick.addEventListener('pointerdown', e => {
    joystickActive = true;
    joystick.classList.add('active');
    joystick.setPointerCapture(e.pointerId);
    moveKnob(e.clientX, e.clientY);
  });
  joystick.addEventListener('pointermove', e => {
    if (!joystickActive) return;
    moveKnob(e.clientX, e.clientY);
  });
  joystick.addEventListener('pointerup', () => {
    joystickActive = false;
    joystick.classList.remove('active');
    knob.style.transform = 'translate(-50%, -50%)';
    lastSent = null; sendCmd('stop');
  });

  // Tab switcher
  function switchTab(name) {
    document.querySelectorAll('.tab').forEach((t,i) => t.classList.toggle('active', ['dpad','joystick'][i] === name));
    document.getElementById('panel-dpad').classList.toggle('visible', name === 'dpad');
    document.getElementById('panel-joystick').classList.toggle('visible', name === 'joystick');
    stopCmd();
  }

  // Safety: stop if page loses focus
  window.addEventListener('blur', stopCmd);
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopCmd(); });
</script>
</body>
</html>
HTMLEOF
