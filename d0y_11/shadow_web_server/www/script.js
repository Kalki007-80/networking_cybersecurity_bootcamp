// Root-level script: wires up the "Ping the server" demo button
document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("ping-btn");
    const resultBox = document.getElementById("ping-result");

    if (!btn || !resultBox) return;

    btn.addEventListener("click", async () => {
        resultBox.textContent = "Loading...";
        try {
            const res = await fetch("/json");
            const data = await res.json();
            resultBox.textContent = JSON.stringify(data, null, 2);
        } catch (err) {
            resultBox.textContent = "Error reaching server: " + err;
        }
    });
});
