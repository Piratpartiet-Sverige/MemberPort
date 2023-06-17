import type { GeoData } from './geography/geodata'

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
  let data: {[k: string]: any} | string | null = null

  if (reason !== undefined && reason != null && reason !== '') {
    data = {
      reason
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
    name
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

export async function sendUpdateAreasRequest (areas: { [id: string]: GeoData }): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/geography/areas', {
    method: 'PUT',
    cache: 'no-cache',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-XSRFToken': xsrf.value
    },
    body: JSON.stringify(areas),
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

export async function sendUpdateMunicipalitiesRequest (municipalities: { [id: string]: GeoData }): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/geography/municipalities', {
    method: 'PUT',
    cache: 'no-cache',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-XSRFToken': xsrf.value
    },
    body: JSON.stringify(municipalities),
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

export async function sendCreateOrganizationRequest (
  name: string,
  description: string,
  active: boolean,
  parentID: string | null,
  countries: string | null,
  areas: string | null,
  municipalities: string | null
): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement
  const data: DataBody = {
    name,
    description,
    active: String(active)
  }

  if (parentID != null) {
    data.parent_id = parentID
  }
  if (countries != null) {
    data.countries = countries
  }
  if (areas != null) {
    data.areas = areas
  }
  if (municipalities != null) {
    data.municipalities = municipalities
  }

  const body = convertDictToBody(data)
  const response = await fetch('/api/organization', {
    method: 'POST',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-XSRFToken': xsrf.value
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body
  })

  return response
}

export async function sendUpdateOrganizationRequest (
  organizationID: string,
  name: string,
  description: string,
  active: boolean,
  parentID: string | null,
  countries: string | null,
  areas: string | null,
  municipalities: string | null
): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement
  const data: DataBody = {
    name,
    description,
    active: String(active)
  }

  if (parentID != null) {
    data.parent_id = parentID
  }
  if (countries != null) {
    data.countries = countries
  }
  if (areas != null) {
    data.areas = areas
  }
  if (municipalities != null) {
    data.municipalities = municipalities
  }

  const body = convertDictToBody(data)
  const response = await fetch('/api/organization/' + organizationID, {
    method: 'PUT',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-XSRFToken': xsrf.value
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body
  })

  return response
}

export async function sendCreatePostRequest (title: string, content: string): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement
  const data: DataBody = {
    title,
    content
  }

  const body = convertDictToBody(data)
  const response = await fetch('/api/feed/post', {
    method: 'POST',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-XSRFToken': xsrf.value
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body
  })

  return response
}

export async function sendFetchCalendarsRequest (): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/calendars', {
    method: 'GET',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-XSRFToken': xsrf.value
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer'
  })

  return response
}

export async function sendCreateCalendarRequest (description: string | null, url: string | null): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement
  const data: DataBody = {}

  if (description !== null) {
    data.description = description
  }
  if (url !== null) {
    data.url = url
  }

  const body = convertDictToBody(data)

  const response = await fetch('/api/calendar', {
    method: 'POST',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-XSRFToken': xsrf.value
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body
  })

  return response
}

export async function sendUpdateCalendarRequest (id: string, description: string | null, url: string | null): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement
  const data: DataBody = {}

  if (description !== null) {
    data.description = description
  }
  if (url !== null) {
    data.url = url
  }

  const body = convertDictToBody(data)

  const response = await fetch('/api/calendar/' + id, {
    method: 'PUT',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-XSRFToken': xsrf.value
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body
  })

  return response
}

export async function sendDeleteCalendarRequest (id: string): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement

  const response = await fetch('/api/calendar/' + id, {
    method: 'DELETE',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-XSRFToken': xsrf.value
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer'
  })

  return response
}

export async function sendHealthRequest (): Promise<Response> {
  const response = await fetch('/api/health', {
    method: 'GET',
    cache: 'no-cache',
    credentials: 'same-origin',
    redirect: 'follow',
    referrerPolicy: 'no-referrer'
  })

  return response
}
