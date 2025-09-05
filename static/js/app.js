console.log("App JS cargado correctamente.");
document.getElementById("btn-saludo")?.addEventListener("click", () => {
  console.log("¡Hola desde JavaScript!");
  alert("¡Hola desde JavaScript!");
});

// ===== Carrusel básico (auto-slide, flechas, dots, swipe) =====
(() => {
  const track = document.querySelector(".car-track");
  if (!track) return;

  const slides = Array.from(track.children);
  const nextBtn = document.querySelector(".car-btn.next");
  const prevBtn = document.querySelector(".car-btn.prev");
  const dots = Array.from(document.querySelectorAll(".car-dots button"));
  const viewport = document.querySelector(".car-viewport");

  let idx = 0;
  let timer;

  function go(to) {
    idx = (to + slides.length) % slides.length;
    track.style.transform = `translateX(-${idx * 100}%)`;
    dots.forEach((d, i) => d.classList.toggle("is-active", i === idx));
  }

  function startAuto() {
    stopAuto();
    timer = setInterval(() => go(idx + 1), 5000);
  }
  function stopAuto() {
    if (timer) clearInterval(timer);
  }

  // Eventos
  nextBtn?.addEventListener("click", () => { go(idx + 1); startAuto(); });
  prevBtn?.addEventListener("click", () => { go(idx - 1); startAuto(); });
  dots.forEach(d => d.addEventListener("click", () => { go(+d.dataset.to); startAuto(); }));

  // Pausa al pasar el mouse o enfocar
  [viewport, nextBtn, prevBtn].forEach(el => {
    el?.addEventListener("mouseenter", stopAuto);
    el?.addEventListener("mouseleave", startAuto);
    el?.addEventListener("focusin", stopAuto);
    el?.addEventListener("focusout", startAuto);
  });

  // Swipe en móvil
  let startX = 0, dx = 0, dragging = false;
  viewport.addEventListener("touchstart", (e) => {
    dragging = true;
    startX = e.touches[0].clientX;
    stopAuto();
  }, {passive:true});
  viewport.addEventListener("touchmove", (e) => {
    if (!dragging) return;
    dx = e.touches[0].clientX - startX;
  }, {passive:true});
  viewport.addEventListener("touchend", () => {
    if (!dragging) return;
    if (dx > 50) go(idx - 1);
    else if (dx < -50) go(idx + 1);
    dragging = false; dx = 0; startAuto();
  });

  // Teclado
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") { go(idx + 1); startAuto(); }
    if (e.key === "ArrowLeft")  { go(idx - 1); startAuto(); }
  });

  // Init
  go(0);
  startAuto();
})();
