// theme.js
function toggleDarkMode() {
    var elements = document.querySelectorAll('body, .sidebar, .content');
    elements.forEach(element => {
        element.classList.toggle("dark-mode");
    });

    if (elements[0].classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
    } else {
        localStorage.setItem("theme", "light");
    }
}

window.onload = function() {
    if (localStorage.getItem("theme") === "dark") {
        var elements = document.querySelectorAll('body, .sidebar, .content');
        elements.forEach(element => {
            element.classList.add("dark-mode");
        });
    }
}