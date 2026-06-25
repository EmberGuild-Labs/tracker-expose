document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("scan-form");
    if (!form) return;

    form.addEventListener("submit", function () {
        var btn = document.getElementById("scan-btn");
        btn.disabled = true;
        btn.textContent = "Scanning…";
        form.classList.add("loading");
    });
});
