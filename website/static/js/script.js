function toggleMenu() {
  const menu = document.querySelector(".menu-links");
  const icon = document.querySelector(".hamburger-icon");
  const open = menu.classList.toggle("open");
  icon.classList.toggle("open", open);
  icon.setAttribute("aria-expanded", String(open));
  icon.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
}

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && document.querySelector(".menu-links.open")) {
    toggleMenu();
    document.querySelector(".hamburger-icon").focus();
  }
});

document.addEventListener("click", (event) => {
  if (!event.target.closest(".hamburger-menu") && document.querySelector(".menu-links.open")) {
    toggleMenu();
  }
});
