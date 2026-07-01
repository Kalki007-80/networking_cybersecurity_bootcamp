// Shared front-end helpers for the Shadow Web Server static site.
const ShadowApp = {
    async getStatus() {
        const res = await fetch("/status");
        return res.json();
    },

    async sayHello(name) {
        const res = await fetch("/hello?name=" + encodeURIComponent(name));
        return res.text();
    },

    logVisit() {
        console.log(
            "%cShadow Web Server%c — static page loaded at " + new Date().toLocaleTimeString(),
            "color:#00d4ff;font-weight:bold;",
            "color:inherit;"
        );
    }
};

ShadowApp.logVisit();
