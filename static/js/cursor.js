(function () {
    const dot  = document.getElementById("cursor-dot");
    const ring = document.getElementById("cursor-ring");
    if (!dot || !ring) return;

    let ringX = 0, ringY = 0;

    document.addEventListener("mousemove", (e) => {
        dot.style.left  = e.clientX + "px";
        dot.style.top   = e.clientY + "px";
        ringX += (e.clientX - ringX) * 0.12;
        ringY += (e.clientY - ringY) * 0.12;
        ring.style.left = ringX + "px";
        ring.style.top  = ringY + "px";
    });

    document.addEventListener("mousedown", () => ring.classList.add("clicking"));
    document.addEventListener("mouseup",   () => ring.classList.remove("clicking"));

    document.addEventListener("click", (e) => {
        const ping = document.createElement("div");
        ping.className = "cursor-ping";
        ping.style.left = e.clientX + "px";
        ping.style.top  = e.clientY + "px";
        document.body.appendChild(ping);
        ping.addEventListener("animationend", () => ping.remove());
    });
})();
