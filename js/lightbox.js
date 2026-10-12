/* Foto ampliada: a original só é baixada quando a pessoa clica numa miniatura.
   Não há pré-carregamento das fotos vizinhas de propósito, para poupar dados. */
(function () {
  'use strict';

  var links = Array.prototype.slice.call(document.querySelectorAll('.gallery a.ph'));
  if (!links.length) return;

  var idx = 0, lb, stage, img, status, count, btnPrev, btnNext, btnClose, lastFocus, touchX = null;

  var SVG = 'width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';
  var ICON = {
    close: '<svg ' + SVG + '><path d="M5 5l14 14M19 5L5 19"/></svg>',
    prev:  '<svg ' + SVG + '><path d="M15 5l-7 7 7 7"/></svg>',
    next:  '<svg ' + SVG + '><path d="M9 5l7 7-7 7"/></svg>'
  };

  function button(cls, label, svg, handler) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'lb-btn ' + cls;
    b.setAttribute('aria-label', label);
    b.innerHTML = svg;
    b.addEventListener('click', function (e) { e.stopPropagation(); handler(); });
    return b;
  }

  function build() {
    lb = document.createElement('div');
    lb.className = 'lb';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Foto ampliada');

    stage = document.createElement('div');
    stage.className = 'lb-stage';

    img = document.createElement('img');
    img.className = 'lb-img';
    img.alt = '';

    status = document.createElement('div');
    status.className = 'lb-status';
    status.setAttribute('role', 'status');

    count = document.createElement('div');
    count.className = 'lb-count';

    btnClose = button('lb-close', 'Cerrar', ICON.close, close);
    btnPrev  = button('lb-prev', 'Anterior', ICON.prev, function () { show(idx - 1); });
    btnNext  = button('lb-next', 'Siguiente', ICON.next, function () { show(idx + 1); });

    stage.appendChild(img);
    stage.appendChild(status);
    lb.appendChild(stage);
    lb.appendChild(count);
    lb.appendChild(btnPrev);
    lb.appendChild(btnNext);
    lb.appendChild(btnClose);
    document.body.appendChild(lb);

    if (links.length < 2) { btnPrev.hidden = true; btnNext.hidden = true; }

    lb.addEventListener('click', function (e) {
      if (e.target === lb || e.target === stage) close();
    });

    lb.addEventListener('touchstart', function (e) {
      touchX = e.changedTouches[0].clientX;
    }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (touchX === null || links.length < 2) return;
      var dx = e.changedTouches[0].clientX - touchX;
      touchX = null;
      if (Math.abs(dx) > 50) show(dx < 0 ? idx + 1 : idx - 1);
    }, { passive: true });
  }

  function show(i) {
    idx = (i + links.length) % links.length;
    var link = links[idx];
    var src = link.href;
    var thumb = link.querySelector('img');

    img.classList.remove('ready');
    status.hidden = false;
    status.textContent = 'Cargando…';
    count.textContent = (idx + 1) + ' / ' + links.length;

    var loader = new Image();
    loader.onload = function () {
      if (links[idx].href !== src) return;   // a pessoa já passou para outra foto
      img.src = src;
      img.alt = thumb ? thumb.alt : '';
      img.classList.add('ready');
      status.hidden = true;
    };
    loader.onerror = function () {
      if (links[idx].href !== src) return;
      status.textContent = 'No se pudo cargar la foto.';
    };
    loader.src = src;
  }

  function open(i) {
    if (!lb) build();
    lastFocus = document.activeElement;
    lb.classList.add('open');
    document.body.classList.add('lb-open');
    show(i);
    btnClose.focus();
  }

  function close() {
    lb.classList.remove('open');
    document.body.classList.remove('lb-open');
    img.removeAttribute('src');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  links.forEach(function (a, i) {
    a.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;  // abrir em nova aba continua funcionando
      e.preventDefault();
      open(i);
    });
  });

  document.addEventListener('keydown', function (e) {
    if (!lb || !lb.classList.contains('open')) return;
    if (e.key === 'Escape') { close(); }
    else if (e.key === 'ArrowLeft' && links.length > 1) { show(idx - 1); }
    else if (e.key === 'ArrowRight' && links.length > 1) { show(idx + 1); }
    else if (e.key === 'Tab') {
      // mantém o foco dentro da janela ampliada
      var ativos = [btnPrev, btnNext, btnClose].filter(function (b) { return !b.hidden; });
      var pos = ativos.indexOf(document.activeElement);
      e.preventDefault();
      var prox = e.shiftKey ? pos - 1 : pos + 1;
      ativos[(prox + ativos.length) % ativos.length].focus();
    }
  });
})();
