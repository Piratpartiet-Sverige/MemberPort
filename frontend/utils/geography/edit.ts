import { GeoData, GEO_TYPES, getNodeType } from './geodata'
import { sendUpdateCountryDataRequest, sendUpdateAreaDataRequest, sendUpdateMunicipalityDataRequest } from '../api'
import { createMessage } from '../ui'

export function sendChangeNameRequest (id: string, geodata: { [id: string]: GeoData }): void {
  const node = document.getElementById(id)
  const newNameInput = document.getElementById('newName') as HTMLInputElement

  if (node === null || newNameInput === null) {
    return
  }

  const newName = newNameInput.value

  const nodeType = getNodeType(id, geodata)
  geodata[id].name = newName

  if (nodeType === GEO_TYPES.COUNTRY) {
    renameCountry(id, newName, geodata)
  } else if (nodeType === GEO_TYPES.AREA) {
    renameArea(id, newName, geodata)
  } else if (nodeType === GEO_TYPES.MUNICIPALITY) {
    renameMunicipality(id, newName, geodata)
  }
}

function changeNodeName (id: string, newName: string, geodata: { [id: string]: GeoData }): boolean {
  const node = document.getElementById(id)

  if (node === null) {
    return false
  }

  geodata[id].name = newName
  const nameBox = node.getElementsByClassName('content')[0] as HTMLElement
  nameBox.innerText = newName
  return true
}

function renameCountry (id: string, newName: string, geodata: { [id: string]: GeoData }): void {
  sendUpdateCountryDataRequest(id, newName)
    .then(async (response: Response) => {
      return await response.json()
    })
    .then((data: { [name: string]: any }) => {
      if (data.success === false) {
        throw new Error(data.reason)
      } else if (!changeNodeName(id, newName, geodata)) {
        throw new Error('NODE NOT FOUND')
      }

      createMessage('Ändrat namn på landet till: ' + newName, 'is-success')
    }).catch((error: string) => {
      console.error('Error:', error)
      createMessage('Någonting gick fel när namnet på landet skulle uppdateras', 'is-danger')
    })
}

function renameArea (id: string, newName: string, geodata: { [id: string]: GeoData }): void {
  sendUpdateAreaDataRequest(id, newName, null, null)
    .then(async function (response: Response) {
      return await response.json()
    })
    .then(function (data: { [name: string]: any }) {
      if (data.success === false) {
        throw new Error(data.reason)
      } else if (!changeNodeName(id, newName, geodata)) {
        throw new Error('NODE NOT FOUND')
      }

      createMessage('Ändrat namn på området till: ' + newName, 'is-success')
    }).catch((error: string) => {
      console.error('Error:', error)
      createMessage('Någonting gick fel när namnet på området skulle uppdateras', 'is-danger')
    })
}

function renameMunicipality (id: string, newName: string, geodata: { [id: string]: GeoData }): void {
  sendUpdateMunicipalityDataRequest(id, newName, null, null)
    .then(async function (response: Response) {
      return await response.json()
    })
    .then(function (data: { [name: string]: any }) {
      if (data.success === false) {
        throw new Error(data.reason)
      } else if (!changeNodeName(id, newName, geodata)) {
        throw new Error('NODE NOT FOUND')
      }

      createMessage('Ändrat namn på kommunen till: ' + newName, 'is-success')
    }).catch((error: string) => {
      console.error('Error:', error)
      createMessage('Någonting gick fel när namnet på kommunen skulle uppdateras', 'is-danger')
    })
}
