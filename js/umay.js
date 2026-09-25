/* ============================================
   umay.dev - Theme Toggle — content is rendered in HTML
   ============================================ */

(function () {
  // --- Theme Toggle ---
  const toggle = document.getElementById('themeToggle');
  const html = document.documentElement;

  // Load saved theme or default to dark
  try {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || saved === 'light') html.setAttribute('data-theme', saved);
  } catch (_) {
    // Browsing modes that block storage still get a working theme toggle.
  }

  if (toggle) {
    toggle.addEventListener('click', function () {
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (_) {}
    });
  }

  document.querySelectorAll('.project-gallery').forEach(function (gallery) {
    const track = gallery.querySelector('.project-preview');
    const controls = gallery.querySelector('.gallery-controls');
    const buttons = controls.querySelectorAll('button');
    function update() {
      const end = track.scrollWidth - track.clientWidth;
      controls.hidden = end < 2;
      buttons[0].disabled = track.scrollLeft < 2;
      buttons[1].disabled = track.scrollLeft >= end - 2;
    }
    buttons.forEach(function (button) {
      button.addEventListener('click', function () {
        track.scrollBy({
          left: Number(button.dataset.direction) * track.clientWidth * 0.8,
          behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
        });
      });
    });
    track.addEventListener('scroll', update, { passive: true });
    track.querySelectorAll('img').forEach(function (img) { img.addEventListener('load', update); });
    if ('ResizeObserver' in window) new ResizeObserver(update).observe(track);
    else window.addEventListener('resize', update);
    update();
  });
})();
