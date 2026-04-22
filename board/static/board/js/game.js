(() => {
  const el = (id) => document.getElementById(id);
  const tiles = JSON.parse(el("tiles-data").textContent);
  const grid = el("board-grid");

  /* ============================================================
   * FIX POINTER-EVENTS: semua wrapper 3D = none, hanya .tile = auto
   * Ini bypass cache CSS / specificity — diterapkan langsung via JS
   * ============================================================ */
  const WRAPPER_SELECTORS = [
    ".app",
    ".stage",
    ".board-shell",
    ".board-pivot",
    ".board-tilt",
    ".board-mass",
    ".board-field",
    ".board-grid",
    ".board-field__mid",
  ];
  for (const sel of WRAPPER_SELECTORS) {
    const node = document.querySelector(sel);
    if (node) node.style.setProperty("pointer-events", "none", "important");
  }
  /* Tile itu sendiri harus bisa diklik */
  for (const tileEl of document.querySelectorAll(".tile")) {
    tileEl.style.setProperty("pointer-events", "auto", "important");
  }
  /* HUD buttons juga harus bisa diklik */
  const HUD_BTNS = ["btn-roll", "die-a", "die-b", "btn-ganjil", "btn-genap"];
  for (const btnId of HUD_BTNS) {
    const btn = el(btnId);
    if (btn) btn.style.setProperty("pointer-events", "auto", "important");
  }
  const hubFloat = el("board-hub-float");
  if (hubFloat) hubFloat.style.setProperty("pointer-events", "none", "important");
  /* ============================================================ */

  for (const t of tiles) {
    const cell = document.querySelector(`.tile[data-index="${t.index}"]`);
    if (!cell) continue;
    cell.style.gridRow = String(t.grid_row);
    cell.style.gridColumn = String(t.grid_col);
    cell.style.setProperty("--card-turn", `${Math.round(Number(t.card_turn_deg) || 0)}deg`);
    if (t.color) cell.style.setProperty("--strip", t.color);
  }
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
    /* showModal() pada dialog yang sudah open = InvalidStateError (mis. klik petak saat gerak token) */
    if (typeof modal.showModal === "function" && !modal.open) modal.showModal();
  }

  function setActive(index) {
    for (const node of document.querySelectorAll(".tile.is-active")) {
      node.classList.remove("is-active");
    }
    const cell = document.querySelector(`.tile[data-index="${index}"]`);
    if (cell) cell.classList.add("is-active");
    const t = tiles[index];
    if (positionLabel) positionLabel.textContent = t.name;
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
  dieA?.addEventListener("click", (e) => {
    e.stopPropagation();
    void activateRoll();
  });
  dieB?.addEventListener("click", (e) => {
    e.stopPropagation();
    void activateRoll();
  });
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

  /*
   * Klik petak: delegation di .board-grid + elementsFromPoint bila target bukan .tile
   * (img/teks/ tumpukan 3D). HUD .board-hub-float tetap pointer-events:none kecuali tombol.
   */
  const boardMass = el("board-mass");

  function eventTargetElement(ev) {
    const raw = ev.target;
    if (raw instanceof Element) return raw;
    if (raw && raw.parentElement) return raw.parentElement;
    return null;
  }

  /** Petak di bawah pointer (termasuk tumpukan 3D / target bukan .tile langsung). */
  function pickTileFromEvent(ev) {
    if (!grid) return null;
    const from = eventTargetElement(ev);
    if (from) {
      const direct = from.closest(".tile");
      if (direct && grid.contains(direct)) return direct;
    }
    const cx = ev.clientX;
    const cy = ev.clientY;
    if (typeof cx !== "number" || typeof cy !== "number") return null;
    if (typeof document.elementsFromPoint !== "function") return null;
    const stack = document.elementsFromPoint(cx, cy);
    if (!stack?.length) return null;
    for (const node of stack) {
      if (!(node instanceof Element)) continue;
      const t = node.closest(".tile");
      if (t && grid.contains(t)) return t;
    }
    return null;
  }

  grid?.addEventListener("click", (e) => {
    const tile = pickTileFromEvent(e);
    if (!tile) return;
    e.preventDefault();
    e.stopPropagation();
    const idx = Number(tile.dataset.index);
    if (!Number.isFinite(idx) || idx < 0 || idx >= tiles.length) return;
    openModal(tiles[idx]);
  });

  /*
   * Fallback capture-phase listener di document: menangkap klik yang "jatuh" di luar
   * .board-grid karena hit-test offset 3D (mis. petak 11–23 di sisi atas diamond).
   * Bekerja dengan elementsFromPoint → cari .tile paling dekat.
   */
  document.addEventListener(
    "click",
    (e) => {
      /* Jika sudah ditangani grid (target ada di dalam .tile) — lewati */
      if (e.target instanceof Element && e.target.closest(".tile")) return;
      /* Hanya area papan */
      const shell = document.querySelector(".board-shell");
      if (!shell) return;
      const sr = shell.getBoundingClientRect();
      if (
        e.clientX < sr.left - 60 ||
        e.clientX > sr.right + 60 ||
        e.clientY < sr.top - 60 ||
        e.clientY > sr.bottom + 60
      )
        return;
      /* Jangan ganggu HUD atau modal */
      if (e.target instanceof Element) {
        if (e.target.closest("#board-hub-float")) return;
        if (e.target.closest(".modal")) return;
        if (e.target.closest("#orbit-dock")) return;
      }
      /* elementsFromPoint — cari .tile paling atas */
      const stack = document.elementsFromPoint(e.clientX, e.clientY);
      let found = null;
      for (const node of stack) {
        if (!(node instanceof Element)) continue;
        const t = node.closest(".tile");
        if (t && grid?.contains(t)) {
          found = t;
          break;
        }
      }
      if (!found) {
        /* Tidak ketemu lewat stack — cari .tile terdekat secara geometri */
        const allTiles = [...document.querySelectorAll(".tile")];
        let minDist = Infinity;
        for (const tEl of allTiles) {
          const r = tEl.getBoundingClientRect();
          if (r.width === 0 || r.height === 0) continue;
          const cx = r.left + r.width / 2;
          const cy = r.top + r.height / 2;
          const dx = e.clientX - cx;
          const dy = e.clientY - cy;
          /* Hanya petak yang sudah dekat dengan kursor (threshold 60 × rasio ukuran) */
          const threshold = Math.max(r.width, r.height) * 0.72;
          const dist = Math.hypot(dx, dy);
          if (dist < threshold && dist < minDist) {
            minDist = dist;
            found = tEl;
          }
        }
      }
      if (!found) return;
      e.stopPropagation();
      const idx = Number(found.dataset.index);
      if (!Number.isFinite(idx) || idx < 0 || idx >= tiles.length) return;
      openModal(tiles[idx]);
    },
    true /* capture — tangkap sebelum stopPropagation di level lain */,
  );

  function onBoardMassPointerDown(e) {
    if (e.pointerType === "mouse" && e.button !== 0) return;

    /* Petak: modal dibuka lewat click di .board-grid (lebih konsisten di atas img / 3D). */

    /* 1. Deteksi klik pada tombol board (HUD) via pointerdown */
    const btn = eventTargetElement(e)?.closest("button");
    if (btn) {
      if (btn === btnRoll || btn === dieA || btn === dieB) {
        e.stopPropagation();
        e.preventDefault();
        void activateRoll();
      } else if (btn === btnGanjil) {
        e.stopPropagation();
        e.preventDefault();
        setParity("ganjil");
      } else if (btn === btnGenap) {
        e.stopPropagation();
        e.preventDefault();
        setParity("genap");
      }
    }
  }
  
  /* Tidak menggunakan phase "capture" lagi, percayakan native bubble */
  boardMass?.addEventListener("pointerdown", onBoardMassPointerDown);

  setActive(0);
  placeTokenOnCell(0);

  /** Kontrol orbit 3D — seret = akumulasi yaw/pitch (tak terbatas); Shift+seret = roll Z */
  const LS_ORBIT_V3 = "mono.board3d.v4"; /* v4: default pitch 50° + persp 2200 */
  const LS_ORBIT_V2 = "mono.board3d.v2";
  const LS_ORBIT_V1 = "mono.board3d.v1";
  /** Default panel orbit: Y:0° X:50° Z:0°; perspektif dekat 2200px */
  const DEFAULT_ORBIT_YAW = 0;
  const DEFAULT_ORBIT_PITCH = 50;
  const DEFAULT_ORBIT_ROLL = 0;
  const DEFAULT_ORBIT_PERSP = 2200;
  /** Pitch berlebihan = petak pojok terlalu menciut seperti "dilihat dari samping" */
  const MAX_PITCH = 68;
  const ORBIT_PERSP_MIN = 2200;
  const ORBIT_PERSP_MAX = 20000;
  /** Nilai yang dipakai versi joystick lama (v2) untuk pitch dari posisi knob */
  const MAX_PITCH_V2 = 26;
  const DEAD_ZONE = 0.12;
  const SENS_YAW = 0.42;
  const SENS_PITCH = 0.32;
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
    return m ? Math.round(Number.parseFloat(m[1])) : 16500;
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
    if (orbitPersp) orbitPersp.value = String(DEFAULT_ORBIT_PERSP);
    if (orbitKnob) orbitKnob.style.transform = "translate(0px, 0px)";
    root.style.setProperty("--board-3d-persp", `${DEFAULT_ORBIT_PERSP}px`);
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
          const persp = Math.max(ORBIT_PERSP_MIN, Math.min(ORBIT_PERSP_MAX, Math.round(o.persp / 100) * 100));
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
      const persp = Math.max(ORBIT_PERSP_MIN, Math.min(ORBIT_PERSP_MAX, Math.round(o.persp / 100) * 100));
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
        Math.max(ORBIT_PERSP_MIN, Math.min(ORBIT_PERSP_MAX, Math.round(stored.persp / 100) * 100)),
      );
    } else if (orbitPersp) {
      orbitYaw = DEFAULT_ORBIT_YAW;
      orbitPitchExtra = DEFAULT_ORBIT_PITCH;
      orbitRoll = DEFAULT_ORBIT_ROLL;
      orbitPersp.value = String(DEFAULT_ORBIT_PERSP);
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

  orbitJoystick?.addEventListener("pointerdown", onJoyPointerDown);
  orbitJoystick?.addEventListener("pointermove", onJoyPointerMove);
  orbitJoystick?.addEventListener("pointerup", onJoyPointerUp);
  orbitJoystick?.addEventListener("pointercancel", onJoyPointerUp);

  orbitJoystick?.addEventListener("keydown", (e) => {
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

  orbitToggle?.addEventListener("click", (e) => {
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
