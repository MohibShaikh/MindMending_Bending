function showModal(overlayClass, formClass) {
    document.querySelector(`.${overlayClass}`).classList.add('showoverlay');
    document.querySelector(`.${formClass}`).classList.add('showloginform');
}

function closeModal(overlayClass, formClass) {
    document.querySelector(`.${overlayClass}`).classList.remove('showoverlay');
    document.querySelector(`.${formClass}`).classList.remove('showloginform');
}

function showConfirmationOverlay(facilityName) {
    // Check if the user is authenticated
    var isAuthenticated = {% if user.is_authenticated %}true{% else %}false{% endif %};

    // If user is authenticated, show overlay and ask for confirmation
    if (isAuthenticated) {
        var confirmation = confirm("Are you sure you want to book " + facilityName + "?");

        // If confirmed, redirect based on the user's choice
        if (confirmation) {
            window.location.href = "{% url 'index' %}";
        }
    } else {
        // If not authenticated, redirect to the authentication page
        window.location.href = "{% url 'auth' %}";
    }
}

var closeBtn1 = document.querySelector('.close1');
closeBtn1.addEventListener("click", function () {
    closeModal('overlay1', 'bookform');
});

var btnLogin = document.querySelector('.btn-login');
btnLogin.addEventListener("click", function () {
    showModal('overlay', 'loginform');
});

var closeBtn = document.querySelector('.close');
closeBtn.addEventListener("click", function () {
    closeModal('overlay', 'loginform');
});

var btnLogin1 = document.querySelector('.btn-login1');
btnLogin1.addEventListener("click", function () {
    showModal('overlay1', 'bookform');
});

var closeBtn1 = document.querySelector('.close1');
closeBtn1.addEventListener("click", function () {
    closeModal('overlay1', 'bookform');
});
