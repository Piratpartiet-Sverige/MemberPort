function toggleYesNoButton(y) {
    var x = document.getElementById(y);
    if (x.innerHTML === "Ja") {
        x.innerHTML = "Nej";
    } else {
        x.innerHTML = "Ja";
    }
}

function togglebutton(id) {
    if (document.getElementById(id).classList.contains('is-success')) {
        document.getElementById(id).classList.remove('is-success'); document.getElementById(id).classList.add('is-danger');
    }
    else {
        document.getElementById(id).classList.remove('is-danger'); document.getElementById(id).classList.add('is-success')
    }
}