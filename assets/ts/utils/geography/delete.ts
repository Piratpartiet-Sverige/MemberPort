import { sendDeleteAreaRequest, sendDeleteCountryRequest, sendDeleteMunicipalityRequest } from '../api'
import { GeoData, GEO_TYPES, getNodeType } from './geodata'
import { createMessage } from '../ui'

export function sendDeleteNodeRequest (id: string, geodata: {[id: string]: GeoData}): void {
  const nodeType = getNodeType(id, geodata)
  const name = geodata[id].name

  if (nodeType === GEO_TYPES.COUNTRY) {
    deleteCountry(id, name)
  } else if (nodeType === GEO_TYPES.AREA) {
    deleteArea(id, name)
  } else if (nodeType === GEO_TYPES.MUNICIPALITY) {
    deleteMunicipality(id, name)
  }
}

export function deleteNode (id: string): boolean {
  const node = document.getElementById(id)

  if (node !== null) {
    node.remove()
    return true
  }

  return false
}

function deleteArea (id: string, name: string): void {
  sendDeleteAreaRequest(id)
    .then(async function (response: Response) {
      if (response.status === 403) {
        throw new Error('ORGANIZATION ACTIVE')
      }

      return await response.json()
    })
    .then(function (data: { [name: string]: any }) {
      if (data.success === false) {
        throw new Error(data.reason)
      } else if (!deleteNode(id)) {
        throw new Error('NODE NOT FOUND')
      }
      createMessage('Raderat området: ' + name, 'is-success')
    }).catch((error: Error) => {
      console.error('Error:', error)

      if (error.message === 'ORGANIZATION ACTIVE') {
        createMessage('Kan inte ta bort området om det finns en organisation kvar i den', 'is-danger')
      } else {
        createMessage('Någonting gick fel när området skulle raderas', 'is-danger')
      }
    })
}

function deleteCountry (id: string, name: string): void {
  sendDeleteCountryRequest(id)
    .then(async function (response: Response) {
      if (response.status === 403) {
        throw new Error('ORGANIZATION ACTIVE')
      }

      return await response.json()
    })
    .then(function (data: { [name: string]: any }) {
      if (data.success === false) {
        throw new Error(data.reason)
      } else if (!deleteNode(id)) {
        throw new Error('NODE NOT FOUND')
      }

      createMessage('Raderat landet: ' + name, 'is-success')
    }).catch((error: Error) => {
      console.error('Error:', error)

      if (error.message === 'ORGANIZATION ACTIVE') {
        createMessage('Kan inte ta bort landet om det finns en organisation kvar i den', 'is-danger')
      } else {
        createMessage('Någonting gick fel när landet skulle raderas', 'is-danger')
      }
    })
}

function deleteMunicipality (id: string, name: string): void {
  sendDeleteMunicipalityRequest(id)
    .then(async function (response: Response) {
      if (response.status === 403) {
        throw new Error('ORGANIZATION ACTIVE')
      }

      return await response.json()
    })
    .then(function (data: { [name: string]: any }) {
      if (data.success === false) {
        throw new Error(data.reason)
      } else if (!deleteNode(id)) {
        throw new Error('NODE NOT FOUND')
      }

      createMessage('Raderat kommunen: ' + name, 'is-success')
    }).catch((error: Error) => {
      console.error('Error:', error)

      if (error.message === 'ORGANIZATION ACTIVE') {
        createMessage('Kan inte ta bort kommunen om det finns en organisation kvar i den', 'is-danger')
      } else {
        createMessage('Någonting gick fel när kommunen skulle raderas', 'is-danger')
      }
    })
}
