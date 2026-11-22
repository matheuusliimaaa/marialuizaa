(() => {
  const KEY = 'pequenos-retratos-temas-seleccionados';
  const read = () => { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; } };
  let selected = read();
  const save = () => localStorage.setItem(KEY, JSON.stringify(selected));
  const bar = document.createElement('aside');
  bar.className = 'selection-bar';
  bar.hidden = true;
  bar.setAttribute('aria-live', 'polite');
  bar.innerHTML = '<span class="selection-count"></span><div class="selection-actions"><button class="selection-clear" type="button">Limpiar</button><button class="selection-send" type="button">Enviar mi selección por WhatsApp</button></div>';
  document.body.appendChild(bar);
  const count = bar.querySelector('.selection-count');
  const sync = () => {
    document.querySelectorAll('.select-theme').forEach(button => {
      const name = button.closest('.theme-card')?.querySelector('h2')?.textContent.trim();
      const active = selected.some(item => item.name === name);
      button.setAttribute('aria-pressed', String(active));
      button.textContent = active ? 'Seleccionado ✓' : 'Seleccionar';
    });
    bar.hidden = selected.length === 0;
    document.body.classList.toggle('has-selection-bar', selected.length > 0);
    count.textContent = selected.length === 1 ? '1 tema seleccionado' : selected.length + ' temas seleccionados';
  };
  document.addEventListener('click', event => {
    const button = event.target.closest('.select-theme');
    if (!button) return;
    const name = button.closest('.theme-card')?.querySelector('h2')?.textContent.trim();
    if (!name) return;
    const index = selected.findIndex(item => item.name === name);
    if (index >= 0) selected.splice(index, 1);
    else selected.push({ name });
    save();
    sync();
  });
  bar.querySelector('.selection-clear').addEventListener('click', () => { selected = []; save(); sync(); });
  bar.querySelector('.selection-send').addEventListener('click', () => {
    if (!selected.length) return;
    const lines = selected.map((item, index) => (index + 1) + '. ' + item.name).join('\\n\\n');
    const message = lines;
    window.open('https://wa.me/?text=' + encodeURIComponent(message), '_blank', 'noopener');
  });
  sync();
})();