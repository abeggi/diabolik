// Theme toggle
(function() {
    const saved = localStorage.getItem('diabolik-theme');
    if (saved === 'dark') {
        document.documentElement.classList.add('dark');
    }

    window.toggleTheme = function() {
        const root = document.documentElement;
        const isDark = root.classList.toggle('dark');
        localStorage.setItem('diabolik-theme', isDark ? 'dark' : 'light');
        updateThemeButton();
    };

    window.updateThemeButton = function() {
        const btn = document.getElementById('theme-btn');
        if (!btn) return;
        const isDark = document.documentElement.classList.contains('dark');
        btn.textContent = isDark ? '🌞 Chiaro' : '🌙 Scuro';
    };

    document.addEventListener('DOMContentLoaded', updateThemeButton);
})();

// Navbar
function renderNavbar(currentPage) {
    const nav = document.createElement('nav');
    nav.className = 'navbar';
    nav.innerHTML = `
        <a href="/" class="logo">DIABOLIK <span>Archive</span></a>
        <a href="/">🏠 Home</a>
        <a href="/impostazioni">⚙️ Impostazioni</a>
        <div class="spacer"></div>
        <button class="theme-toggle" id="theme-btn" onclick="toggleTheme()">🌙 Scuro</button>
    `;
    document.body.prepend(nav);
    updateThemeButton();
}

// Cover URL helper
function coverUrl(copertinaLocale) {
    if (!copertinaLocale) return null;
    return '/covers/' + copertinaLocale;
}

// Fallback on image error
function imgFallback(el, titolo) {
    el.onerror = null;
    var placeholder = document.createElement('div');
    placeholder.className = 'cover';
    placeholder.textContent = titolo || '';
    el.replaceWith(placeholder);
}

// Debounce
function debounce(fn, ms) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), ms);
    };
}

// API helpers
async function api(url) {
    const resp = await fetch(url);
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: resp.statusText }));
        throw new Error(err.detail || resp.statusText);
    }
    return resp.json();
}

async function apiPost(url, body) {
    const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined,
    });
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: resp.statusText }));
        throw new Error(err.detail || resp.statusText);
    }
    return resp.json();
}

async function apiDelete(url) {
    const resp = await fetch(url, { method: 'DELETE' });
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: resp.statusText }));
        throw new Error(err.detail || resp.statusText);
    }
    return resp.json();
}

function showToast(message, type) {
    type = type || 'success';
    var old = document.querySelector('.toast-overlay');
    if (old) old.remove();

    var overlay = document.createElement('div');
    overlay.className = 'toast-overlay';
    overlay.innerHTML = '<div class="toast-box toast-' + type + '">' + message + '</div>';
    document.body.appendChild(overlay);

    overlay.addEventListener('click', function() { overlay.remove(); });
    setTimeout(function() {
        overlay.style.opacity = '0';
        setTimeout(function() { overlay.remove(); }, 300);
    }, 2500);
}
