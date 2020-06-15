function toggleInput(inputID) {
    if (document.getElementById(inputID).classList.contains('is-static')) {
        document.getElementById(inputID).classList.remove('is-static');
        document.getElementById(inputID).removeAttribute('readonly');
    } else {
        document.getElementById(inputID).classList.add('is-static');
        document.getElementById(inputID).setAttribute('readonly', '');
    }
}

function toggleHidden(buttonID) {
    if (document.getElementById(buttonID).classList.contains('is-hidden')) {
        document.getElementById(buttonID).classList.remove('is-hidden');
    } else {
        document.getElementById(buttonID).classList.add('is-hidden');
    }
}

function toggleSaveButton(buttonID) {
    var button = document.getElementById(buttonID);
    if (button.innerHTML === "Ändra") {
        button.innerHTML = "Spara";
    } else {
        button.innerHTML = "Ändra";
        
        sendRequest()
            .then(response => {
                console.log(response);
                console.log(response.statusText);
                if (response.ok) {
                    var successElement = document.getElementById("successText");
                    successElement.innerHTML = "Ändringar sparade";
                    document.getElementById("successNotification").style.display = "block";
                }
            });
    }
}

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

async function sendRequest() {
    var form = document.getElementById("settings");
    const formData = new FormData(form);

    const response = await fetch(form.getAttribute("action"), {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'same-origin',
        body: new URLSearchParams(formData)
    });

    return response;
}