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

    // ----- 0) Inyectar link "Usuarios" si el rol es admin y no existe ya -----
    if (document.body.classList.contains("role-admin")) {
      var nav = sidebar.querySelector(".sidebar-nav");
      var yaExiste = sidebar.querySelector('a[href="/usuarios"]');
      if (nav && !yaExiste) {
        var ajustes = sidebar.querySelector('a[href="/ajustes"]');
        var link = document.createElement("a");
        link.className = "nav-item";
        link.href = "/usuarios";
        if (window.location.pathname.indexOf("/usuarios") === 0) {
          link.classList.add("active");
        }
        link.innerHTML =
          '<svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" ' +
          'viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">' +
          '<path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z"/>' +
          '</svg><span class="nav-text">Usuarios</span>';
        if (ajustes) {
          nav.insertBefore(link, ajustes);
        } else {
          nav.appendChild(link);
        }
      }
    }

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

    // En escritorio el menú permanece fijo; en móvil se cierra tras navegar.
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
