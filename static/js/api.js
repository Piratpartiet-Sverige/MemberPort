function updateMunicipalities() {
    sendMunicipalityRequest()
        .then(response => response.json())
        .then(response => {
            const municipalities = document.getElementById("traits.municipality");

            while (municipalities.firstChild) {
                municipalities.removeChild(municipalities.firstChild);
            }

            var newHTML = "<option disabled selected value>Välj din kommun</option>";

            for (const [id, municipality] of Object.entries(response.data)) {
                newHTML += "<option value=\"" + municipality.name + "\">" + municipality.name + "</option>\n";
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