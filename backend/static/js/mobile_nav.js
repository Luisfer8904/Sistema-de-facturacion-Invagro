/* ============================================================
 * mobile_nav.js
 * Sistema Invagro · Navegación móvil
 *
 * Inyecta un botón hamburguesa en el topbar y convierte el
 * sidebar lateral en un "drawer" deslizable cuando la pantalla
 * es pequeña. No requiere cambios en plantillas individuales.
 * ============================================================ */
(function () {
  if (window.__invagroMobileNavInit) return;
  window.__invagroMobileNavInit = true;

  function init() {
    var sidebar = document.querySelector(".sidebar");
    var topbar = document.querySelector(".topbar");

    // Si la página no tiene sidebar/topbar (ej. login, landing), no hacemos nada
    if (!sidebar || !topbar) return;

    // ----- 1) Crear el botón hamburguesa -----
    var btn = document.createElement("button");
    btn.className = "mobile-menu-toggle";
    btn.type = "button";
    btn.setAttribute("aria-label", "Abrir menú");
    btn.setAttribute("aria-expanded", "false");
    btn.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="M3 6h18M3 12h18M3 18h18"/></svg>';

    var topbarLeft = topbar.querySelector(".topbar-left");
    if (topbarLeft) {
      topbarLeft.insertBefore(btn, topbarLeft.firstChild);
    } else {
      topbar.insertBefore(btn, topbar.firstChild);
    }

    // ----- 2) Crear backdrop (capa oscura detrás del drawer) -----
    var backdrop = document.createElement("div");
    backdrop.className = "mobile-sidebar-backdrop";
    backdrop.setAttribute("aria-hidden", "true");
    document.body.appendChild(backdrop);

    // ----- 3) Funciones para abrir/cerrar -----
    function open() {
      document.body.classList.add("sidebar-open");
      btn.setAttribute("aria-expanded", "true");
    }
    function close() {
      document.body.classList.remove("sidebar-open");
      btn.setAttribute("aria-expanded", "false");
    }
    function toggle(e) {
      if (e) e.stopPropagation();
      if (document.body.classList.contains("sidebar-open")) close();
      else open();
    }

    // ----- 4) Eventos -----
    btn.addEventListener("click", toggle);
    backdrop.addEventListener("click", close);

    // Cerrar al tocar cualquier enlace de navegación dentro del sidebar
    var navLinks = sidebar.querySelectorAll(".nav-item, a[href]");
    for (var i = 0; i < navLinks.length; i++) {
      navLinks[i].addEventListener("click", function () {
        // Solo cierra si estamos en modo móvil (drawer activo)
        if (window.matchMedia("(max-width: 900px)").matches) close();
      });
    }

    // Cerrar con tecla Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("sidebar-open")) {
        close();
      }
    });

    // Si la ventana se agranda y entramos en desktop, cerrar el drawer
    window.addEventListener("resize", function () {
      if (window.innerWidth > 900 && document.body.classList.contains("sidebar-open")) {
        close();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
