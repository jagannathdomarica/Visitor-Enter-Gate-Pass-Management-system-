class Toast {
    constructor() {
        this.container = document.createElement("div");
        this.container.className = "toast-container";
        document.body.appendChild(this.container);
    }

    show(message, type = "info", duration = 4000) {
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        const icon = document.createElement("span");
        icon.className = "toast-icon";
        icon.textContent = type === "success" ? "&#10003;" : type === "error" ? "&#9888;" : "&#128172;";
        const text = document.createElement("span");
        text.textContent = message;
        const close = document.createElement("span");
        close.className = "toast close";
        close.innerHTML = "&times;";
        close.onclick = () => this.remove(toast);
        toast.appendChild(icon);
        toast.appendChild(text);
        toast.appendChild(close);
        this.container.appendChild(toast);
        setTimeout(() => toast.classList.add("show"), 10);
        setTimeout(() => this.remove(toast), duration);
    }

    remove(toast) {
        toast.classList.remove("show");
        setTimeout(() => {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 300);
    }

    success(message, duration) { this.show(message, "success", duration); }
    error(message, duration) { this.show(message, "error", duration); }
    info(message, duration) { this.show(message, "info", duration); }
}

const toast = new Toast();

function showModal(modalEl, formEl) {
    modalEl.classList.add("active");
    document.body.style.overflow = "hidden";
    if (formEl) formEl.reset();
}

function hideModal(modalEl, formEl) {
    modalEl.classList.remove("active");
    document.body.style.overflow = "";
    if (formEl) formEl.reset();
}

function setLoading(btn, isLoading) {
    if (isLoading) {
        btn.disabled = true;
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner"></span> ' + btn.dataset.originalText;
    } else {
        btn.disabled = false;
        btn.innerHTML = btn.dataset.originalText || btn.innerHTML.replace(/<span class="spinner"><\/span>\s*/, '');
    }
}

function setButtonLoading(btn, isLoading) {
    if (isLoading) {
        btn.disabled = true;
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner"></span> ' + btn.dataset.originalText;
    } else {
        btn.disabled = false;
        btn.innerHTML = btn.dataset.originalText;
    }
}

function attachModal(modalSelector, openBtnSelector, closeBtnSelector, formResetSelector) {
    const modal = document.querySelector(modalSelector);
    const openBtn = document.querySelector(openBtnSelector);
    const closeBtn = document.querySelector(closeBtnSelector);
    const form = formResetSelector ? document.querySelector(formResetSelector) : null;

    if (openBtn) {
        openBtn.addEventListener("click", () => showModal(modal, form));
    }
    if (closeBtn) {
        closeBtn.addEventListener("click", () => hideModal(modal, form));
    }
    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) hideModal(modal, form);
        });
    }
    return { modal, openBtn, closeBtn, form };
}

function attachSearch(inputSelector, rowSelector) {
    const input = document.querySelector(inputSelector);
    if (!input) return;
    input.addEventListener("keyup", function () {
        const filter = this.value.toLowerCase();
        const rows = document.querySelectorAll(rowSelector);
        rows.forEach((row) => {
            row.style.display = row.textContent.toLowerCase().includes(filter) ? "" : "none";
        });
    });
}

function formatDateTime(dt) {
    if (!dt) return "-";
    return dt;
}
