function ShowModal(){
    document.querySelector('.overlay').classList.add('showoverlay');
    document.querySelector('.loginform').classList.add('showloginform');
}
function CloseModal(){
    document.querySelector('.overlay').classList.remove('showoverlay');
    document.querySelector('.loginform').classList.remove('showloginform');
}
var btnlogin=document.querySelector('.btn-login');
btnlogin.addEventListener("click", ShowModal)

var c=document.querySelector('.close');
c.addEventListener("click", CloseModal)