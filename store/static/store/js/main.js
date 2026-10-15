// BoltSports - UI helpers (presentation only; keep form/filter behaviour)
document.addEventListener('DOMContentLoaded', function () {

    // 1. Close buttons on messages, and auto-hide after 5 seconds
    document.querySelectorAll('.message').forEach(function (message) {
        var closeButton = message.querySelector('.message-close');
        if (closeButton) {
            closeButton.addEventListener('click', function () { message.remove(); });
        }
        setTimeout(function () { message.remove(); }, 5000);
    });

    // 2. Filters on the shop page apply as soon as an option is chosen
    document.querySelectorAll('.auto-submit').forEach(function (select) {
        select.addEventListener('change', function () { select.form.submit(); });
    });

    // 3. Ask for confirmation before submitting forms marked with data-confirm
    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!confirm(form.dataset.confirm)) { event.preventDefault(); }
        });
    });

    // 4. + and - buttons for the quantity box on the product page
    document.querySelectorAll('.qty').forEach(function (box) {
        var input = box.querySelector('input');
        box.querySelectorAll('.qty-btn').forEach(function (button) {
            button.addEventListener('click', function () {
                var min = parseInt(input.min, 10) || 1;
                var max = parseInt(input.max, 10) || 999;
                var value = (parseInt(input.value, 10) || min) + parseInt(button.dataset.step, 10);
                input.value = Math.min(Math.max(value, min), max);
            });
        });
    });

    // 5. Mobile navigation toggle
    var toggle = document.getElementById('nav-toggle');
    var nav = document.getElementById('main-nav');
    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            var open = nav.classList.toggle('is-open');
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            toggle.classList.toggle('is-open', open);
        });
    }
});
