import { sendUpdateOrganizationRequest } from '../utils/api'
import { createMessage } from '../utils/ui'
import { GeoData, GEO_TYPES } from '../utils/geography/geodata'
import { addArea, addCountry, addMunicipality, filter, getCheckedCountries, getCheckedAreas, getCheckedMunicipalities } from '../utils/geography/selection'
import { afterPageLoad } from '../utils/after-page-load'
import '../../sass/geography-selection.scss'

declare let geodata: { [id: string]: GeoData }
declare let countryID: string
declare let organizationID: string

function getParentID (id: string, path: string, fallbackID: string): string {
  let parentID = ''

  if (path === id) {
    parentID = fallbackID
  } else {
    const pathList = path.split('.')

    if (pathList.length < 2) {
      parentID = fallbackID
    } else {
      parentID = pathList[pathList.length - 2]
    }
  }

  return parentID
}

afterPageLoad().then(() => {
  let parentID = ''
  addCountry(countryID, geodata[countryID].name, 'recruitmentArea', geodata)

  for (const id in geodata) {
    const data = geodata[id]

    // Check if this is an area
    if (data.type === GEO_TYPES.AREA && data.path !== undefined) {
      parentID = getParentID(data.id, data.path, countryID)
      addArea(data.id, data.name, parentID, geodata)
    } else if (data.type === GEO_TYPES.MUNICIPALITY && data.area !== undefined) { // Municipality
      parentID = data.area

      if (parentID === '') {
        parentID = countryID
      }

      addMunicipality(data.id, data.name, parentID, geodata)
    }
  }

  const search = document.getElementById('searchArea') as HTMLInputElement
  if (search !== null) {
    search.oninput = function () {
      filter(search.value)
    }
  }

  const saveButton = document.getElementById('saveButton') as HTMLButtonElement
  saveButton.onclick = function () {
    const nameElements = document.getElementsByName('name')
    const descriptionElements = document.getElementsByName('description')
    const activeElements = document.getElementsByName('active')

    let name = ''
    let description = ''
    let active = false

    if (nameElements.length > 0 && descriptionElements.length > 0 && activeElements.length > 0) {
      const nameElement = nameElements[0] as HTMLInputElement
      const descriptionElement = descriptionElements[0] as HTMLInputElement
      const activeElement = activeElements[0] as HTMLInputElement

      name = nameElement.value
      description = descriptionElement.value
      active = activeElement.checked
    } else {
      return
    }

    const countries = getCheckedCountries('recruitmentArea')
    const areas = getCheckedAreas('recruitmentArea')
    const municipalities = getCheckedMunicipalities('recruitmentArea')

    sendUpdateOrganizationRequest(organizationID, name, description, active, countries, areas, municipalities).then((response: Response) => {
      if (response.ok) {
        createMessage('Ändringarna är sparade!', 'is-success', 'saveButton')
      } else {
        createMessage('Något gick fel när ändringarna skulle sparas', 'is-danger', 'saveButton')
      }
    }).catch((reason) => {
      console.log(reason)
      createMessage('Något gick fel när ändringarna skulle sparas', 'is-danger', 'saveButton')
    })
  }
}).catch(console.error)
