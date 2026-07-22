(() => {
    const root = document.documentElement;
    const toggle = document.getElementById("theme-toggle");
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {
        root.setAttribute("data-bs-theme", "dark");
        toggle.textContent = "Light mode";
    }

    toggle?.addEventListener("click", () => {
        const isDark = root.getAttribute("data-bs-theme") === "dark";
        root.setAttribute("data-bs-theme", isDark ? "light" : "dark");
        localStorage.setItem("theme", isDark ? "light" : "dark");
        toggle.textContent = isDark ? "Dark mode" : "Light mode";
    });

    document.querySelectorAll("[data-table-search]").forEach((input) => {
        const table = document.querySelector(input.dataset.tableSearch);
        input.addEventListener("input", () => {
            const query = input.value.trim().toLowerCase();
            table?.querySelectorAll("tbody tr").forEach((row) => {
                row.hidden = !row.textContent.toLowerCase().includes(query);
            });
        });
    });
})();
