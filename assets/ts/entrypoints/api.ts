interface DataBody {
  [index: string]: string
}

function convertDictToBody (dict: DataBody): string {
  return Object.keys(dict).map(key => encodeURIComponent(key) + '=' + encodeURIComponent(dict[key])).join('&')
}

export function updateMunicipalities (): void {
  sendMunicipalityRequest()
    .then(async (response: Response) => {
      return await response.json()
    })
    .then((response: { [name: string]: any }) => {
      const municipalities = document.getElementById('traits.municipality')
      if (municipalities == null) {
        return
      }

      while (municipalities.firstChild != null) {
        municipalities.removeChild(municipalities.firstChild)
      }

      const selectedValue = municipalities.dataset.value

      let newHTML = '<option disabled selected value>Välj din kommun</option>'

      for (const [id, municipality] of Object.entries<DataBody>(response.data)) {
        const selectedStr = selectedValue === municipality.name ? ' selected' : ''
        newHTML += '<option value="' + municipality.name + '" ' + selectedStr + '>' + municipality.name + '</option>\n'
      }

      municipalities.innerHTML = newHTML
    })
    .catch((error: string) => {
      console.error(error)
    })
}

export async function sendMunicipalityRequest (): Promise<Response> {
  const country = document.getElementById('traits.country') as HTMLInputElement
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/geography/municipalities?country=' + country.value, {
    method: 'GET',
    cache: 'no-cache',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-XSRFToken': xsrf.value
    },
    redirect: 'error',
    referrerPolicy: 'same-origin'
  })

  return response
}

export async function sendMembershipRequest (userID: string, orgID: string): Promise<Response> {
  const data = {
    organization: orgID,
    user: userID
  }

  const dataBody = convertDictToBody(data)
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/membership', {
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
  })

  return response
}

export async function sendEndMembershipRequest (membershipID: string, reason: string): Promise<Response> {
  let data = null

  if (reason !== undefined && reason != null && reason !== '') {
    data = {
      reason: reason
    }

    data = convertDictToBody(data)
  }

  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/membership/' + membershipID, {
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
  })

  return response
}

export async function sendUpdateCountryDataRequest (countryID: string, name: string): Promise<Response> {
  const data = {
    name: name
  }

  const dataBody = convertDictToBody(data)
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/geography/country/' + countryID, {
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
  })

  return response
}

export async function sendUpdateAreaDataRequest (areaID: string, name: string | null, countryID: string | null, path: string | null): Promise<Response> {
  const data: DataBody = {
    area_id: areaID
  }

  if (name !== null && name !== undefined) {
    data.name = name
  }

  if (countryID !== null && countryID !== undefined) {
    data.country_id = countryID
  }

  if (path !== null && path !== undefined) {
    data.path = path
  }

  const dataBody = convertDictToBody(data)
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/geography/area/' + areaID, {
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
  })

  return response
}

export async function sendUpdateMunicipalityDataRequest (municipalityID: string, name: string | null, countryID: string | null, areaID: string | null): Promise<Response> {
  const data: DataBody = {
    municipality_id: municipalityID
  }

  if (name !== null && name !== undefined) {
    data.name = name
  }

  if (countryID !== null && countryID !== undefined) {
    data.country_id = countryID
  }

  if (areaID !== null && areaID !== undefined) {
    data.area_id = areaID
  }

  const dataBody = convertDictToBody(data)
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/geography/municipality/' + municipalityID, {
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
  })

  return response
}

export async function sendDeleteCountryRequest (countryID: string): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/geography/country/' + countryID, {
    method: 'DELETE',
    cache: 'no-cache',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-XSRFToken': xsrf.value
    },
    body: null,
    redirect: 'error',
    referrerPolicy: 'same-origin'
  })

  return response
}

export async function sendDeleteAreaRequest (areaID: string): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/geography/area/' + areaID, {
    method: 'DELETE',
    cache: 'no-cache',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-XSRFToken': xsrf.value
    },
    body: null,
    redirect: 'error',
    referrerPolicy: 'same-origin'
  })

  return response
}

export async function sendDeleteMunicipalityRequest (municipalityID: string): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/geography/municipality/' + municipalityID, {
    method: 'DELETE',
    cache: 'no-cache',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-XSRFToken': xsrf.value
    },
    body: null,
    redirect: 'error',
    referrerPolicy: 'same-origin'
  })

  return response
}
