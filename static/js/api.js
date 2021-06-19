function convertDictToBody(dict) {
    return Object.keys(dict).map(key => encodeURIComponent(key) + '=' + encodeURIComponent(dict[key])).join('&');
}

function updateMunicipalities() {
    sendMunicipalityRequest()
        .then(response => response.json())
        .then(response => {
            const municipalities = document.getElementById("traits.municipality");

            while (municipalities.firstChild) {
                municipalities.removeChild(municipalities.firstChild);
            }

            var selectedValue = municipalities.dataset.value

            var newHTML = "<option disabled selected value>Välj din kommun</option>";

            for (const [id, municipality] of Object.entries(response.data)) {
                var selectedStr = selectedValue === municipality.name ? ' selected' : ''
                newHTML += "<option value=\"" + municipality.name + "\" " + selectedStr + ">" + municipality.name + "</option>\n";
            }

            municipalities.innerHTML = newHTML;
        });
}

async function sendMunicipalityRequest() {
    var country = document.getElementById("traits.country");

    const response = await fetch("/api/geography/municipalities?country=" + country.value, {
        method: 'GET',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-XSRFToken': document.getElementsByName("_xsrf")[0].value
        },
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}

async function sendMembershipRequest(user_id, org_id) {
    var data = {
        "organization": org_id,
        "user": user_id
    }

    data = convertDictToBody(data);

    const response = await fetch("/api/membership", {
        method: 'POST',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-XSRFToken': document.getElementsByName("_xsrf")[0].value
        },
        body: data,
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}

async function sendEndMembershipRequest(membership_id, reason) {
    var data = null;

    if (reason != undefined && reason != null && reason !== "") {
        data = {
            "reason": reason
        }
    
        data = convertDictToBody(data);
    }

    console.log(data);

    const response = await fetch("/api/membership/" + membership_id, {
        method: 'DELETE',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-XSRFToken': document.getElementsByName("_xsrf")[0].value
        },
        body: data,
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}

async function sendUpdateCountryDataRequest(country_id, name) {
    var data = {
        "name": name
    }
    
    data = convertDictToBody(data);

    const response = await fetch("/api/geography/country/" + country_id, {
        method: 'PUT',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-XSRFToken': document.getElementsByName("_xsrf")[0].value
        },
        body: data,
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}

async function sendUpdateAreaDataRequest(area_id, name, country_id, path) {
    var data = {
        "name": name,
        "country_id": country_id,
        "path": path
    }

    data = convertDictToBody(data);

    const response = await fetch("/api/geography/area/" + area_id, {
        method: 'PUT',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-XSRFToken': document.getElementsByName("_xsrf")[0].value
        },
        body: data,
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}

async function sendUpdateMunicipalityDataRequest(municipality_id, name, country_id, area_id) {
    var data = {
        "name": name,
        "country_id": country_id,
        "area_id": area_id
    }

    data = convertDictToBody(data);

    const response = await fetch("/api/geography/municipality/" + municipality_id, {
        method: 'PUT',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-XSRFToken': document.getElementsByName("_xsrf")[0].value
        },
        body: data,
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}
