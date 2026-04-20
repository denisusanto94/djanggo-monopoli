(() => {
  const el = (id) => document.getElementById(id);
  const tiles = JSON.parse(el("tiles-data").textContent);
  const grid = el("board-grid");
  const token = el("token");
  const dieA = el("die-a");
  const dieB = el("die-b");
  const btnRoll = el("btn-roll");
  const btnGanjil = el("btn-ganjil");
  const btnGenap = el("btn-genap");
  const positionLabel = el("position-label");
  const modal = el("tile-modal");
  const modalTitle = el("modal-title");
  const modalBody = el("modal-body");

  let pos = 0;
  let moving = false;

  const tileEls = () => [...document.querySelectorAll(".tile")].sort(
    (a, b) => Number(a.dataset.index) - Number(b.dataset.index),
  );

  function describeTile(t) {
    const bits = [`Jenis: ${t.kind}`];
    if (t.price) bits.push(`Harga tanah: Rp ${t.price.toLocaleString("id-ID")}`);
    return bits.join(" · ");
  }

  function openModal(t) {
    modalTitle.textContent = t.name;
    modalBody.textContent = describeTile(t);
    if (typeof modal.showModal === "function") modal.showModal();
  }

  function setActive(index) {
    for (const node of document.querySelectorAll(".tile.is-active")) {
      node.classList.remove("is-active");
    }
    const cell = document.querySelector(`.tile[data-index="${index}"]`);
    if (cell) cell.classList.add("is-active");
    const t = tiles[index];
    positionLabel.textContent = t.name;
  }

  function placeTokenOnCell(index) {
    const cell = document.querySelector(`.tile[data-index="${index}"]`);
    if (!cell || !grid) return;
    token.classList.add("visible");
    /* getBoundingClientRect = layar setelah transform; left/top = koordinat lokal grid → token “melorot” */
    const x = cell.offsetLeft + cell.offsetWidth / 2;
    const y = cell.offsetTop + cell.offsetHeight / 2;
    token.style.left = `${x}px`;
    token.style.top = `${y}px`;
  }

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  async function moveSteps(steps) {
    moving = true;
    btnRoll.disabled = true;
    for (let i = 0; i < steps; i += 1) {
      pos = (pos + 1) % tiles.length;
      setActive(pos);
      placeTokenOnCell(pos);
      await sleep(120);
    }
    moving = false;
    btnRoll.disabled = false;
  }

  function rollDice() {
    const a = 1 + Math.floor(Math.random() * 6);
    const b = 1 + Math.floor(Math.random() * 6);
    dieA.textContent = String(a);
    dieB.textContent = String(b);
    return a + b;
  }

  function setParity(which) {
    if (!btnGanjil || !btnGenap) return;
    btnGanjil.classList.toggle("is-active", which === "ganjil");
    btnGenap.classList.toggle("is-active", which === "genap");
  }

  btnGanjil?.addEventListener("click", () => setParity("ganjil"));
  btnGenap?.addEventListener("click", () => setParity("genap"));
  setParity("genap");

  let lastRollAt = 0;
  async function activateRoll() {
    const now = Date.now();
    if (moving || now - lastRollAt < 450) return;
    lastRollAt = now;
    const steps = rollDice();
    await moveSteps(steps);
    openModal(tiles[pos]);
  }

  btnRoll?.addEventListener("click", (e) => {
    e.stopPropagation();
    void activateRoll();
  });
  btnRoll?.addEventListener("keydown", (e) => {
    if (e.key === " " || e.key === "Enter") {
      e.preventDefault();
      void activateRoll();
    }
  });

  /* 3D + pointer-events: lubang tengah — cadangan hit-test lewat rect layar */
  const boardMass = el("board-mass");
  const HIT_PAD = 18;
  function rectHit(node, x, y) {
    if (!node) return false;
    const r = node.getBoundingClientRect();
    if (!r.width && !r.height) return false;
    return (
      x >= r.left - HIT_PAD &&
      x <= r.right + HIT_PAD &&
      y >= r.top - HIT_PAD &&
      y <= r.bottom + HIT_PAD
    );
  }
  function hubPickAtClient(x, y) {
    if (rectHit(btnGanjil, x, y)) return "ganjil";
    if (rectHit(btnGenap, x, y)) return "genap";
    if (rectHit(btnRoll, x, y)) return "roll";
    return null;
  }
  function onBoardMassPointerDownCapture(e) {
    if (e.pointerType === "mouse" && e.button !== 0) return;
    const hit = hubPickAtClient(e.clientX, e.clientY);
    if (!hit) return;
    e.stopPropagation();
    if (hit === "roll") void activateRoll();
    else if (hit === "ganjil") setParity("ganjil");
    else if (hit === "genap") setParity("genap");
  }
  boardMass?.addEventListener("pointerdown", onBoardMassPointerDownCapture, true);

  for (const cell of tileEls()) {
    cell.addEventListener("click", () => {
      const idx = Number(cell.dataset.index);
      openModal(tiles[idx]);
    });
  }

  setActive(0);
  placeTokenOnCell(0);

  /** Kontrol orbit 3D — seret = akumulasi yaw/pitch (tak terbatas); Shift+seret = roll Z */
  const LS_ORBIT_V3 = "mono.board3d.v3";
  const LS_ORBIT_V2 = "mono.board3d.v2";
  const LS_ORBIT_V1 = "mono.board3d.v1";
  /** Default panel orbit: Y:0° X:45° Z:0° (sama dengan reset & :root); HUD membatalkan pitch X lewat CSS */
  const DEFAULT_ORBIT_YAW = 0;
  const DEFAULT_ORBIT_PITCH = 45;
  const DEFAULT_ORBIT_ROLL = 0;
  const MAX_PITCH = 78;
  /** Nilai yang dipakai versi joystick lama (v2) untuk pitch dari posisi knob */
  const MAX_PITCH_V2 = 26;
  const DEAD_ZONE = 0.12;
  const SENS_YAW = 0.42;
  const SENS_PITCH = 0.38;
  const SENS_ROLL = 0.45;
  const KNOB_MOVE_SCALE = 28;

  const orbitDock = document.getElementById("orbit-dock");
  const orbitToggle = document.getElementById("orbit-toggle");
  const orbitPanel = document.getElementById("orbit-panel");
  const orbitJoystick = document.getElementById("orbit-joystick");
  const orbitKnob = document.getElementById("orbit-joystick-knob");
  const orbitPersp = document.getElementById("orbit-persp");
  const orbitReset = document.getElementById("orbit-reset");
  const orbitPerspVal = document.getElementById("orbit-persp-val");
  const orbitReadYaw = document.getElementById("orbit-read-yaw");
  const orbitReadPitch = document.getElementById("orbit-read-pitch");
  const orbitReadRoll = document.getElementById("orbit-read-roll");
  const root = document.documentElement;

  let orbitYaw = DEFAULT_ORBIT_YAW;
  let orbitPitchExtra = DEFAULT_ORBIT_PITCH;
  let orbitRoll = DEFAULT_ORBIT_ROLL;
  let joyDragging = false;
  let knobNx = 0;
  let knobNy = 0;

  function readBasePerspective() {
    const raw = getComputedStyle(root).getPropertyValue("--iso-perspective").trim();
    const m = /^([\d.]+)px$/i.exec(raw);
    return m ? Math.round(Number.parseFloat(m[1])) : 4200;
  }

  function knobMaxTravelPx() {
    if (!orbitJoystick || !orbitKnob) return 44;
    const jr = orbitJoystick.getBoundingClientRect();
    const kr = orbitKnob.offsetWidth / 2;
    return Math.max(26, Math.min(jr.width, jr.height) / 2 - 10 - kr);
  }

  function clampUnitDisk(nx, ny) {
    const m = Math.hypot(nx, ny);
    if (m <= 1 || m === 0) return { nx, ny };
    return { nx: nx / m, ny: ny / m };
  }

  function clamp(n, lo, hi) {
    return Math.max(lo, Math.min(hi, n));
  }

  function setKnobFromMovement(mx, my) {
    const { nx, ny } = clampUnitDisk(mx / KNOB_MOVE_SCALE, my / KNOB_MOVE_SCALE);
    knobNx = nx;
    knobNy = ny;
    if (orbitKnob) {
      const maxR = knobMaxTravelPx();
      orbitKnob.style.transform = `translate(${nx * maxR}px, ${ny * maxR}px)`;
    }
  }

  function applyOrbitTransforms() {
    root.style.setProperty("--board-3d-y", `${orbitYaw}deg`);
    root.style.setProperty("--board-3d-x-extra", `${orbitPitchExtra}deg`);
    root.style.setProperty("--board-3d-z", `${orbitRoll}deg`);
    if (orbitReadYaw) orbitReadYaw.textContent = `Y: ${Math.round(orbitYaw)}°`;
    if (orbitReadPitch) orbitReadPitch.textContent = `X: ${Math.round(orbitPitchExtra)}°`;
    if (orbitReadRoll) orbitReadRoll.textContent = `Z: ${Math.round(orbitRoll)}°`;
    orbitJoystick?.setAttribute("aria-valuenow", String(Math.round(orbitYaw)));
  }

  function applyPerspectiveOnly() {
    if (!orbitPersp) return;
    const persp = Number(orbitPersp.value);
    root.style.setProperty("--board-3d-persp", `${persp}px`);
    if (orbitPerspVal) orbitPerspVal.textContent = `${persp}px`;
  }

  function persistOrbit() {
    if (!orbitPersp) return;
    const persp = Number(orbitPersp.value);
    try {
      localStorage.setItem(
        LS_ORBIT_V3,
        JSON.stringify({
          v: 3,
          yaw: orbitYaw,
          pitch: orbitPitchExtra,
          roll: orbitRoll,
          persp,
        }),
      );
      localStorage.removeItem(LS_ORBIT_V2);
    } catch (_) {
      /* ignore */
    }
  }

  function applyOrbitAll() {
    applyOrbitTransforms();
    applyPerspectiveOnly();
    persistOrbit();
    placeTokenOnCell(pos);
  }

  function resetOrbit() {
    orbitYaw = DEFAULT_ORBIT_YAW;
    orbitPitchExtra = DEFAULT_ORBIT_PITCH;
    orbitRoll = DEFAULT_ORBIT_ROLL;
    knobNx = 0;
    knobNy = 0;
    if (orbitPersp) orbitPersp.value = String(readBasePerspective());
    if (orbitKnob) orbitKnob.style.transform = "translate(0px, 0px)";
    root.style.removeProperty("--board-3d-persp");
    applyOrbitTransforms();
    applyPerspectiveOnly();
    if (orbitPerspVal && orbitPersp) orbitPerspVal.textContent = `${orbitPersp.value}px`;
    try {
      localStorage.removeItem(LS_ORBIT_V3);
      localStorage.removeItem(LS_ORBIT_V2);
      localStorage.removeItem(LS_ORBIT_V1);
    } catch (_) {
      /* ignore */
    }
    placeTokenOnCell(pos);
  }

  function openOrbitPanel(open) {
    if (!orbitPanel || !orbitToggle) return;
    orbitPanel.hidden = !open;
    orbitToggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) orbitJoystick?.focus();
  }

  function v2DiskToEuler(nx, ny) {
    const c = clampUnitDisk(nx, ny);
    const m = Math.hypot(c.nx, c.ny);
    if (m < DEAD_ZONE) return { yaw: 0, pitch: 0 };
    const yaw = (Math.atan2(c.ny, c.nx) * 180) / Math.PI;
    const pitch = clamp(-c.ny * MAX_PITCH_V2, -MAX_PITCH_V2, MAX_PITCH_V2);
    return { yaw, pitch };
  }

  function migrateLegacyOrbitToV3() {
    try {
      const raw2 = localStorage.getItem(LS_ORBIT_V2);
      if (raw2) {
        const o = JSON.parse(raw2);
        if (o && o.v === 2 && typeof o.nx === "number" && typeof o.ny === "number" && typeof o.persp === "number") {
          const { yaw, pitch } = v2DiskToEuler(o.nx, o.ny);
          orbitYaw = yaw;
          orbitPitchExtra = pitch;
          orbitRoll = 0;
          const persp = Math.max(2200, Math.min(12000, Math.round(o.persp / 100) * 100));
          if (orbitPersp) orbitPersp.value = String(persp);
          localStorage.setItem(
            LS_ORBIT_V3,
            JSON.stringify({ v: 3, yaw: orbitYaw, pitch: orbitPitchExtra, roll: 0, persp }),
          );
          localStorage.removeItem(LS_ORBIT_V2);
          return;
        }
      }
      const raw1 = localStorage.getItem(LS_ORBIT_V1);
      if (!raw1) return;
      const o = JSON.parse(raw1);
      if (typeof o.yaw !== "number" || typeof o.persp !== "number") return;
      const rad = (o.yaw * Math.PI) / 180;
      let nx = Math.cos(rad) * 0.55;
      let ny = Math.sin(rad) * 0.55;
      if (typeof o.tilt === "number") {
        ny -= (o.tilt / 24) * 0.35;
      }
      const { yaw, pitch } = v2DiskToEuler(nx, ny);
      orbitYaw = yaw;
      orbitPitchExtra = pitch;
      orbitRoll = 0;
      const persp = Math.max(2200, Math.min(12000, Math.round(o.persp / 100) * 100));
      if (orbitPersp) orbitPersp.value = String(persp);
      localStorage.setItem(
        LS_ORBIT_V3,
        JSON.stringify({ v: 3, yaw: orbitYaw, pitch: orbitPitchExtra, roll: 0, persp }),
      );
      localStorage.removeItem(LS_ORBIT_V1);
    } catch (_) {
      /* ignore */
    }
  }

  function initOrbit() {
    if (!orbitDock || !orbitToggle || !orbitJoystick || !orbitKnob) return;
    let stored = null;
    try {
      stored = JSON.parse(localStorage.getItem(LS_ORBIT_V3) || "null");
    } catch (_) {
      stored = null;
    }
    if (!stored || stored.v !== 3) migrateLegacyOrbitToV3();
    try {
      stored = JSON.parse(localStorage.getItem(LS_ORBIT_V3) || "null");
    } catch (_) {
      stored = null;
    }
    const base = readBasePerspective();
    if (
      stored &&
      stored.v === 3 &&
      typeof stored.yaw === "number" &&
      typeof stored.pitch === "number" &&
      typeof stored.roll === "number" &&
      typeof stored.persp === "number"
    ) {
      orbitYaw = stored.yaw;
      orbitPitchExtra = clamp(stored.pitch, -MAX_PITCH, MAX_PITCH);
      orbitRoll = stored.roll;
      orbitPersp.value = String(
        Math.max(2200, Math.min(12000, Math.round(stored.persp / 100) * 100)),
      );
    } else if (orbitPersp) {
      orbitYaw = DEFAULT_ORBIT_YAW;
      orbitPitchExtra = DEFAULT_ORBIT_PITCH;
      orbitRoll = DEFAULT_ORBIT_ROLL;
      orbitPersp.value = String(base);
    }
    knobNx = 0;
    knobNy = 0;
    if (orbitKnob) orbitKnob.style.transform = "translate(0px, 0px)";
    applyOrbitAll();
  }

  function onJoyPointerDown(e) {
    if (!orbitJoystick || e.button === 2) return;
    joyDragging = true;
    orbitJoystick.setPointerCapture(e.pointerId);
    e.preventDefault();
  }

  function onJoyPointerMove(e) {
    if (!joyDragging || !orbitJoystick?.hasPointerCapture(e.pointerId)) return;
    const mx = e.movementX;
    const my = e.movementY;
    if (e.shiftKey) {
      orbitRoll += mx * SENS_ROLL;
    } else {
      orbitYaw += mx * SENS_YAW;
      orbitPitchExtra = clamp(orbitPitchExtra - my * SENS_PITCH, -MAX_PITCH, MAX_PITCH);
    }
    setKnobFromMovement(mx, my);
    applyOrbitTransforms();
    applyPerspectiveOnly();
    persistOrbit();
    placeTokenOnCell(pos);
    e.preventDefault();
  }

  function onJoyPointerUp(e) {
    if (!orbitJoystick?.hasPointerCapture(e.pointerId)) return;
    joyDragging = false;
    orbitJoystick.releasePointerCapture(e.pointerId);
    knobNx = 0;
    knobNy = 0;
    if (orbitKnob) orbitKnob.style.transform = "translate(0px, 0px)";
    e.preventDefault();
  }

  orbitJoystick.addEventListener("pointerdown", onJoyPointerDown);
  orbitJoystick.addEventListener("pointermove", onJoyPointerMove);
  orbitJoystick.addEventListener("pointerup", onJoyPointerUp);
  orbitJoystick.addEventListener("pointercancel", onJoyPointerUp);

  orbitJoystick.addEventListener("keydown", (e) => {
    const stepYaw = e.shiftKey ? 5.5 : 2.8;
    const stepPitch = e.shiftKey ? 4.5 : 2.2;
    const stepRoll = 4;
    if (e.shiftKey && (e.key === "ArrowLeft" || e.key === "ArrowRight")) {
      orbitRoll += e.key === "ArrowLeft" ? -stepRoll : stepRoll;
      e.preventDefault();
    } else if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      orbitYaw += e.key === "ArrowLeft" ? -stepYaw : stepYaw;
      e.preventDefault();
    } else if (e.key === "ArrowUp" || e.key === "ArrowDown") {
      orbitPitchExtra = clamp(
        orbitPitchExtra + (e.key === "ArrowUp" ? stepPitch : -stepPitch),
        -MAX_PITCH,
        MAX_PITCH,
      );
      e.preventDefault();
    } else {
      return;
    }
    applyOrbitTransforms();
    persistOrbit();
    placeTokenOnCell(pos);
  });

  orbitToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    openOrbitPanel(orbitPanel.hidden);
  });

  document.addEventListener(
    "click",
    (e) => {
      if (!orbitDock || orbitPanel?.hidden) return;
      const t = e.target;
      if (t && typeof t.closest === "function") {
        if (
          t.closest("#board-hub-float") ||
          t.closest("#board-mass") ||
          t.closest("#board-grid") ||
          t.closest(".board-shell")
        ) {
          return;
        }
      }
      if (!orbitDock.contains(t)) openOrbitPanel(false);
    },
    true,
  );

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") openOrbitPanel(false);
  });

  orbitPersp?.addEventListener("input", () => {
    applyPerspectiveOnly();
    persistOrbit();
    placeTokenOnCell(pos);
  });

  orbitReset?.addEventListener("click", () => resetOrbit());

  window.addEventListener("resize", () => {
    placeTokenOnCell(pos);
    if (orbitKnob && joyDragging) {
      const maxR = knobMaxTravelPx();
      orbitKnob.style.transform = `translate(${knobNx * maxR}px, ${knobNy * maxR}px)`;
    }
  });

  initOrbit();
})();
