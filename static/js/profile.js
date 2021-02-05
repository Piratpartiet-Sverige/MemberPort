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

function enableJoinButton() {
    let button = document.getElementById("joinButton");
    button.disabled = false;
}

function setFailureNotification(id, textID, text) {
    let notification = document.getElementById(id);
    let notificationText = document.getElementById(textID);

    if (notification.classList.contains('is-success')) {
        notification.classList.remove('is-success');
    }

    notification.classList.add('is-danger');
    notificationText.textContent = text;
}

function setSuccessNotification(id, textID, text) {
    let notification = document.getElementById(id);
    let notificationText = document.getElementById(textID);

    if (notification.classList.contains('is-danger')) {
        notification.classList.remove('is-danger');
    }

    notification.classList.add('is-success');
    notificationText.textContent = text;
}

function showNotification(id) {
    document.getElementById(id).classList.remove('is-hidden');
}

function hideNotification(id) {
    document.getElementById(id).classList.add('is-hidden');
}

function toggleNotification(id) {
    let notification = document.getElementById(id);
    if (notification.classList.contains('is-hidden')) {
        notification.classList.remove('is-hidden');
    } else {
        notification.classList.add('is-hidden');
    }
}

function joinOrganization(user_id = "") {
    var selectedOrg = document.getElementById("joinOrganization");
    var org_id = selectedOrg.value;
    var org_name = selectedOrg.options[selectedOrg.selectedIndex].text;

    sendMembershipRequest(user_id, org_id)
        .then(response => {
            if (!response.ok) {
                setFailureNotification("joinNotification", "joinText", "Något gick fel när du försökte bli medlem, försök gärna igen");
                showNotification("joinNotification");
                throw new Error('Network response was not ok');
            }

            return response.json()
        })
        .then(response => {
            setSuccessNotification("joinNotification", "joinText", "Du är nu medlem i " + org_name + "!");
            showNotification("joinNotification");
        })
        .catch(error => {
            console.error("Something went wrong when trying to join organization", error);
        });
}
