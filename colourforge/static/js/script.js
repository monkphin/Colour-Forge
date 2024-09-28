document.addEventListener("DOMContentLoaded", function() {
    // sidenav initialization
    let sidenav = document.querySelectorAll(".sidenav");
    M.Sidenav.init(sidenav);
    // carousel initialization
    let carousel = document.querySelectorAll('.carousel');
    M.Carousel.init(carousel);
});
