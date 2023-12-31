function showModal(overlayClass, formClass) {
    document.querySelector(`.${overlayClass}`).classList.add('showoverlay');
    document.querySelector(`.${formClass}`).classList.add('showloginform');
}

function closeModal(overlayClass, formClass) {
    document.querySelector(`.${overlayClass}`).classList.remove('showoverlay');
    document.querySelector(`.${formClass}`).classList.remove('showloginform');
}

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
