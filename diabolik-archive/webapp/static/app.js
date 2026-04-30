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

// Navbar with active link highlighting + mobile hamburger menu
function renderNavbar(currentPage) {
    const nav = document.createElement('nav');
    nav.className = 'navbar';
    nav.innerHTML = `
        <a href="/" class="logo">DIABOLIK <span>Archive</span></a>
        <a href="/" class="nav-link ${currentPage === 'home' ? 'active' : ''}">🏠 Home</a>
        <a href="/impostazioni" class="nav-link ${currentPage === 'settings' ? 'active' : ''}">⚙️ Impostazioni</a>
        <div class="spacer"></div>
        <button class="theme-toggle" id="theme-btn" onclick="toggleTheme()">🌙 Scuro</button>
        <button class="hamburger" id="hamburger-btn" onclick="toggleMobileMenu()" aria-label="Menu">☰</button>
    `;

    const mobileMenu = document.createElement('div');
    mobileMenu.className = 'mobile-menu hidden';
    mobileMenu.id = 'mobile-menu';
    mobileMenu.innerHTML = `
        <a href="/" class="${currentPage === 'home' ? 'active' : ''}">🏠 Home</a>
        <a href="/impostazioni" class="${currentPage === 'settings' ? 'active' : ''}">⚙️ Impostazioni</a>
    `;

    document.body.prepend(mobileMenu);
    document.body.prepend(nav);
    updateThemeButton();

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.navbar') && !e.target.closest('.mobile-menu')) {
            closeMobileMenu();
        }
    });
}

window.toggleMobileMenu = function() {
    const menu = document.getElementById('mobile-menu');
    const btn = document.getElementById('hamburger-btn');
    if (!menu) return;
    const isOpen = !menu.classList.contains('hidden');
    menu.classList.toggle('hidden');
    btn.textContent = isOpen ? '☰' : '✕';
};

function closeMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const btn = document.getElementById('hamburger-btn');
    if (!menu || menu.classList.contains('hidden')) return;
    menu.classList.add('hidden');
    if (btn) btn.textContent = '☰';
}

// Cover URL helper
function coverUrl(copertinaLocale) {
    if (!copertinaLocale) return null;
    return '/covers/' + copertinaLocale;
}

// Fallback on image error — reads title from data-titolo attribute
function imgFallback(el) {
    el.onerror = null;
    var placeholder = document.createElement('div');
    placeholder.className = 'cover';
    placeholder.textContent = el.dataset.titolo || '';
    el.replaceWith(placeholder);
}

// HTML escape for safe innerHTML insertion
function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
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

// Non-blocking snackbar (replaces modal toast overlay)
function showToast(message, type) {
    type = type || 'success';
    var old = document.querySelector('.snackbar');
    if (old) old.remove();

    var snackbar = document.createElement('div');
    snackbar.className = 'snackbar snackbar-' + type;
    snackbar.textContent = message;
    document.body.appendChild(snackbar);

    requestAnimationFrame(function() {
        requestAnimationFrame(function() {
            snackbar.classList.add('snackbar-show');
        });
    });

    setTimeout(function() {
        snackbar.classList.remove('snackbar-show');
        setTimeout(function() { snackbar.remove(); }, 300);
    }, 2500);
}
