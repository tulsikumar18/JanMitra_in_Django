document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".password-toggle").forEach(function (button) {

        button.addEventListener("click", function () {

            const target = document.getElementById(this.dataset.target);

            if (!target) {
                return;
            }

            const icon = this.querySelector("i");

            if (target.type === "password") {

                target.type = "text";

                icon.classList.remove("bi-eye");

                icon.classList.add("bi-eye-slash");

            } else {

                target.type = "password";

                icon.classList.remove("bi-eye-slash");

                icon.classList.add("bi-eye");

            }

        });

    });

});



// fade out Django messages

document.addEventListener("DOMContentLoaded", function () {

    const messages =
        document.querySelectorAll(".glass-message");

    messages.forEach(function (message) {

        setTimeout(function () {

            message.style.transition =
                "opacity 0.4s ease, transform 0.4s ease";

            message.style.opacity = "0";

            message.style.transform =
                "translateX(30px)";

            setTimeout(function () {

                message.remove();

            }, 400);

        }, 5000);

    });

});