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

})();
