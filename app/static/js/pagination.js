// Add to the existing base.html scripts
// Pagination helper - renders Bootstrap pagination and calls callback on page click
function renderPagination(p, containerId, onPageClick) {
    const el = document.getElementById(containerId);
    if (!el) return;
    if (!p || p.pages <= 1) { el.innerHTML = ""; return; }
    
    const page = p.page, pages = p.pages;
    let html = `<div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mt-2">
        <small class="text-muted">共 ${p.total} 条，第 ${page}/${pages} 页</small>
        <ul class="pagination pagination-sm mb-0">`;
    
    // First + Prev
    html += `<li class="page-item ${page <= 1 ? "disabled" : ""}">
        <a class="page-link" href="#" data-page="1">&laquo;</a></li>`;
    html += `<li class="page-item ${page <= 1 ? "disabled" : ""}">
        <a class="page-link" href="#" data-page="${page - 1}">&lsaquo;</a></li>`;
    
    // Page numbers - show window of 5 around current page
    let start = Math.max(1, page - 2);
    let end = Math.min(pages, start + 4);
    if (end - start < 4) start = Math.max(1, end - 4);
    
    if (start > 1) {
        html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
    }
    for (let i = start; i <= end; i++) {
        html += `<li class="page-item ${i === page ? "active" : ""}">
            <a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
    }
    if (end < pages) {
        html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
    }
    
    // Next + Last
    html += `<li class="page-item ${page >= pages ? "disabled" : ""}">
        <a class="page-link" href="#" data-page="${page + 1}">&rsaquo;</a></li>`;
    html += `<li class="page-item ${page >= pages ? "disabled" : ""}">
        <a class="page-link" href="#" data-page="${pages}">&raquo;</a></li>`;
    
    html += `</ul></div>`;
    el.innerHTML = html;
    
    // Attach click handlers
    el.querySelectorAll(".page-link[data-page]").forEach(a => {
        a.addEventListener("click", e => {
            e.preventDefault();
            const pg = parseInt(a.dataset.page);
            if (!isNaN(pg) && pg !== page && pg >= 1 && pg <= pages) {
                onPageClick(pg);
            }
        });
    });
}
