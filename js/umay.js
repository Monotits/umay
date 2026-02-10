/* ============================================
   umay.dev - Theme Toggle + Blog Loader
   ============================================ */

(function () {
  // --- Theme Toggle ---
  const toggle = document.getElementById('themeToggle');
  const html = document.documentElement;

  // Load saved theme or default to dark
  const saved = localStorage.getItem('theme');
  if (saved) {
    html.setAttribute('data-theme', saved);
  }

  if (toggle) {
    toggle.addEventListener('click', function () {
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    });
  }

  // --- Blog Loader ---
  var blogContainer = document.getElementById('blogPosts');
  var blogEmpty = document.getElementById('blogEmpty');

  if (blogContainer) {
    fetch('/blog/posts.json')
      .then(function (res) {
        if (!res.ok) throw new Error('No posts');
        return res.json();
      })
      .then(function (posts) {
        if (!posts || posts.length === 0) {
          blogEmpty.style.display = 'block';
          return;
        }
        posts.sort(function (a, b) {
          return new Date(b.date) - new Date(a.date);
        });
        var html = '';
        posts.forEach(function (post) {
          html += '<a href="/blog/' + post.slug + '.html" class="blog-card">';
          html += '<div class="blog-card-date">' + post.date + '</div>';
          html += '<div class="blog-card-title">' + escapeHtml(post.title) + '</div>';
          html += '<div class="blog-card-excerpt">' + escapeHtml(post.excerpt) + '</div>';
          html += '</a>';
        });
        blogContainer.innerHTML = html;
      })
      .catch(function () {
        if (blogEmpty) blogEmpty.style.display = 'block';
      });
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // --- Simple Markdown Parser (for blog posts) ---
  window.renderMarkdown = function (md) {
    var html = md
      // Code blocks (``` ... ```)
      .replace(/```(\w*)\n([\s\S]*?)```/g, function (_, lang, code) {
        return '<pre><code class="lang-' + lang + '">' + escapeHtml(code.trim()) + '</code></pre>';
      })
      // Headings
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      // Bold & italic
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      // Inline code
      .replace(/`(.+?)`/g, '<code>$1</code>')
      // Images
      .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" loading="lazy" />')
      // Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
      // Blockquotes
      .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
      // Unordered lists
      .replace(/^- (.+)$/gm, '<li>$1</li>')
      // Horizontal rules
      .replace(/^---$/gm, '<hr />')
      // Paragraphs (double newline)
      .replace(/\n\n/g, '</p><p>')
      // Single line breaks
      .replace(/\n/g, '<br />');

    // Wrap list items
    html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
    // Clean up nested ul
    html = html.replace(/<\/ul>\s*<ul>/g, '');

    return '<p>' + html + '</p>';
  };
})();
