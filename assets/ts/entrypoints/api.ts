interface DataBody {
    [index: string]: string;
}

function convertDictToBody(dict: DataBody) {
    return Object.keys(dict).map(key => encodeURIComponent(key) + '=' + encodeURIComponent(dict[key])).join('&');
}

export function updateMunicipalities() {
    sendMunicipalityRequest()
        .then(response => response.json())
        .then(response => {
            const municipalities = document.getElementById("traits.municipality");
            if (municipalities == null) {
                return;
            }

            while (municipalities.firstChild) {
                municipalities.removeChild(municipalities.firstChild);
            }

            var selectedValue = municipalities.dataset.value

            var newHTML = "<option disabled selected value>Välj din kommun</option>";

            for (const [id, municipality] of Object.entries<DataBody>(response.data)) {
                var selectedStr = selectedValue === municipality.name ? ' selected' : ''
                newHTML += "<option value=\"" + municipality.name + "\" " + selectedStr + ">" + municipality.name+ "</option>\n";
            }

            municipalities.innerHTML = newHTML;
        });
}

export async function sendMunicipalityRequest() {
    var country = document.getElementById("traits.country") as HTMLInputElement;
    let xsrf = document.getElementsByName("_xsrf")[0] as HTMLInputElement;

    const response = await fetch("/api/geography/municipalities?country=" + country.value, {
        method: 'GET',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-XSRFToken': xsrf.value
        },
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}

export async function sendMembershipRequest(user_id: string, org_id: string) {
    var data = {
        "organization": org_id,
        "user": user_id
    }

    let dataBody = convertDictToBody(data);
    let xsrf = document.getElementsByName("_xsrf")[0] as HTMLInputElement;

    const response = await fetch("/api/membership", {
        method: 'POST',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-XSRFToken': xsrf.value
        },
        body: dataBody,
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}

export async function sendEndMembershipRequest(membership_id: string, reason: string) {
    var data = null;

    if (reason != undefined && reason != null && reason !== "") {
        data = {
            "reason": reason
        }
    
        data = convertDictToBody(data);
    }

    let xsrf = document.getElementsByName("_xsrf")[0] as HTMLInputElement;

    const response = await fetch("/api/membership/" + membership_id, {
        method: 'DELETE',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-XSRFToken': xsrf.value
        },
        body: data,
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}

export async function sendUpdateCountryDataRequest(country_id: string, name: string): Promise<Response> {
    var data = {
        "name": name
    }
    
    let dataBody = convertDictToBody(data);
    let xsrf = document.getElementsByName("_xsrf")[0] as HTMLInputElement;

    const response = await fetch("/api/geography/country/" + country_id, {
        method: 'PUT',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-XSRFToken': xsrf.value
        },
        body: dataBody,
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}

export async function sendUpdateAreaDataRequest(area_id: string, name: string|null, country_id: string|null, path: string|null): Promise<Response> {
    let data: DataBody;

    data = {
        "area_id": area_id
    };

    if (name !== null && name !== undefined) {
        data["name"] = name;
    }

    if (country_id !== null && country_id !== undefined) {
        data["country_id"] = country_id;
    }

    if (path !== null && path !== undefined) {
        data["path"] = path;
    }

    let dataBody = convertDictToBody(data);
    let xsrf = document.getElementsByName("_xsrf")[0] as HTMLInputElement;

    const response = await fetch("/api/geography/area/" + area_id, {
        method: 'PUT',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-XSRFToken': xsrf.value
        },
        body: dataBody,
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}

export async function sendUpdateMunicipalityDataRequest(municipality_id: string, name: string|null, country_id: string|null, area_id: string|null): Promise<Response> {
    let data: DataBody;

    data = {
        "municipality_id": municipality_id
    };

    if (name !== null && name !== undefined) {
        data["name"] = name;
    }

    if (country_id !== null && country_id !== undefined) {
        data["country_id"] = country_id;
    }

    if (area_id !== null && area_id !== undefined) {
        data["area_id"] = area_id;
    }

    let dataBody = convertDictToBody(data);
    let xsrf = document.getElementsByName("_xsrf")[0] as HTMLInputElement;

    const response = await fetch("/api/geography/municipality/" + municipality_id, {
        method: 'PUT',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-XSRFToken': xsrf.value
        },
        body: dataBody,
        redirect: 'error',
        referrerPolicy: 'same-origin'
    });

    return response;
}
