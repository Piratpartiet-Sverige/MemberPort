try {
    var selectedOrg = document.getElementById("joinOrganization");
    var org_name = selectedOrg.options[selectedOrg.selectedIndex].text;

    if (selectedOrg.options.length === 1) {
        selectedOrg.selectedIndex = 0;
        disableJoinButton();
    }
} catch {
    selectedOrg.selectedIndex = 0;
    disableJoinButton();
}

function toggleYesNoButton(y) {
    var x = document.getElementById(y);
    if (x.innerHTML === "Ja") {
        x.innerHTML = "Nej";
    } else {
        x.innerHTML = "Ja";
    }
}

function toggleModal(id, title) {
    let modal = document.getElementById(id);
    let titleElement = modal.getElementsByClassName("modal-card-title")[0];

    titleElement.textContent = title;

    if (modal.classList.contains('is-active')) {
        modal.classList.remove('is-active');
    } else {
        modal.classList.add('is-active');
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

function disableJoinButton() {
    let button = document.getElementById("joinButton");
    button.disabled = true;
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

            const newRow = "<tr is='membership-row' id='" + response.data.id +
            "' created='" + response.data.created +
            "' renewal='" + response.data.renewal +
            "' org-name='" + org_name +"'></tr>";
            document.getElementById('memberships').insertAdjacentHTML("beforeend", newRow);

            selectedOrg.options[selectedOrg.selectedIndex].remove();
            selectedOrg.selectedIndex = 0;

            if (selectedOrg.options.length === 1) {
                disableJoinButton();
            }
        })
        .catch(error => {
            console.error("Something went wrong when trying to join organization", error);
        });
}

function endMembershipModal(membership_id = "", org_name) {
    toggleModal('reason', "Avsluta medlemskap - " + org_name);
    let endMembershipButton = document.getElementById("endMembershipButton");
    endMembershipButton.onclick = function() {
        endMembership(membership_id, org_name);
    };
}

function endMembership(membership_id, org_name) {
    let reasonElement = document.getElementsByName("reason")[0];
    let reason = reasonElement.value;
    reasonElement.value = "";
    console.log(reason);
    toggleModal('reason', "Avsluta medlemskap - " + org_name);

    sendEndMembershipRequest(membership_id, reason)
        .then(response => {
            if (!response.ok) {
                setFailureNotification("joinNotification", "joinText", "Något gick fel när du försökte avsluta ditt medlemskap, försök gärna igen");
                showNotification("joinNotification");
                throw new Error('Network response was not ok');
            } else {
                document.getElementById(membership_id).remove();
                setSuccessNotification("joinNotification", "joinText", "Du har nu avslutat ditt medlemskap i " + org_name + "");
                showNotification("joinNotification");
            }
        })
        .catch(error => {
            console.error("Something went wrong when trying to join organization", error);
        });
}

class MembershipRow extends HTMLTableRowElement {
    constructor() {
        self = super();

        const name = document.createElement('td');
        const created = document.createElement('td');
        const renewal = document.createElement('td');
        const renew = document.createElement('td');
        const end = document.createElement('td');
        const boldName = document.createElement('b');
        const renewButton = document.createElement('button');
        const endButton = document.createElement('button');
        const orgID = this.id;
        const orgName = this.getAttribute('org-name')

        boldName.textContent = orgName;
        name.append(boldName);
        created.textContent = self.getAttribute('created');
        renewal.textContent = self.getAttribute('renewal');

        renewButton.classList.add("button", "is-success");
        endButton.classList.add("button", "is-danger");
        renewButton.onclick = function() {};

        endButton.onclick = function() {
            endMembershipModal(orgID, orgName);
        };
        renewButton.textContent = "Förnya";
        endButton.textContent = "Avsluta";

        renew.append(renewButton);
        end.append(endButton);

        self.append(name, created, renewal, renew, end);
    }
}

customElements.define('membership-row', MembershipRow, { extends: 'tr' });