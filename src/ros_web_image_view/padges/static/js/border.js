(function () {
    const img = document.getElementById('view');
    const top    = document.getElementById('top-border');
    const bottom = document.getElementById('bottom-border');
    const left   = document.getElementById('left-border');
    const right  = document.getElementById('right-border');

    function cellSize() {
        const probe = document.createElement('span');
        const cs = getComputedStyle(top);
        probe.style.font = cs.font;
        probe.style.whiteSpace = 'pre';
        probe.style.position = 'absolute';
        probe.style.visibility = 'hidden';
        probe.textContent = '-'.repeat(100);
        document.body.appendChild(probe);
        const r = probe.getBoundingClientRect();
        document.body.removeChild(probe);
        return {w: r.width / 100, h: r.height};
    }

    function draw() {
        if (!img.offsetWidth) return;
        const {w, h} = cellSize();
        const cols = Math.round(img.offsetWidth / w);
        const rows = Math.round(img.offsetHeight / h);
        const bar = '+' + '-'.repeat(cols + 2) + '+';
        top.textContent = bar;
        bottom.textContent = bar;
        left.textContent = Array(rows).fill('|').join('\n');
        right.textContent = Array(rows).fill('|').join('\n');
    }

    const schedule = () => requestAnimationFrame(draw);

    if (img.complete && img.naturalWidth) schedule();
    img.addEventListener('load', schedule);
    window.addEventListener('resize', schedule);

    if ('ResizeObserver' in window) new ResizeObserver(schedule).observe(img);
})();