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
    const g = grid.getBoundingClientRect();
    const r = cell.getBoundingClientRect();
    token.classList.add("visible");
    token.style.left = `${r.left - g.left + r.width / 2}px`;
    token.style.top = `${r.top - g.top + r.height / 2}px`;
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

  btnRoll.addEventListener("click", async () => {
    if (moving) return;
    const steps = rollDice();
    await moveSteps(steps);
    openModal(tiles[pos]);
  });

  for (const cell of tileEls()) {
    cell.addEventListener("click", () => {
      const idx = Number(cell.dataset.index);
      openModal(tiles[idx]);
    });
  }

  window.addEventListener("resize", () => placeTokenOnCell(pos));

  setActive(0);
  placeTokenOnCell(0);
})();
