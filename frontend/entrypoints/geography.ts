import '../sass/geography.scss'
import { GeoData, GEO_TYPES } from '../utils/geography/geodata'
import { addArea, addCountry, addMunicipality } from '../utils/geography/add'
import * as ui from '../utils/geography/ui'
import { afterPageLoad } from '../utils/after-page-load'

declare let geodata: { [id: string]: GeoData }
declare let selectedCountryID: string

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
  addCountry(selectedCountryID, geodata[selectedCountryID].name, geodata)
  let parentID = ''

  for (const id in geodata) {
    const data = geodata[id]

    // Check if this is an area
    if (data.type === GEO_TYPES.AREA && data.path !== undefined) {
      parentID = getParentID(data.id, data.path, selectedCountryID)
      addArea(data.id, data.name, parentID, geodata)
    } else if (data.type === GEO_TYPES.MUNICIPALITY && data.area !== undefined) { // Municipality
      parentID = data.area

      if (parentID === '') {
        parentID = selectedCountryID
      }

      addMunicipality(data.id, data.name, parentID, geodata)
    }
  }

  const cancelDeleteSmall = document.getElementById('cancelDeleteSmall')
  if (cancelDeleteSmall !== null) {
    cancelDeleteSmall.onclick = () => { ui.closeDeleteModal() }
  }

  const cancelDelete = document.getElementById('cancelDelete')
  if (cancelDelete !== null) {
    cancelDelete.onclick = () => { ui.closeDeleteModal() }
  }

  const cancelEditSmall = document.getElementById('cancelEditSmall')
  if (cancelEditSmall !== null) {
    cancelEditSmall.onclick = () => { ui.closeEditModal() }
  }

  const cancelEdit = document.getElementById('cancelEdit')
  if (cancelEdit !== null) {
    cancelEdit.onclick = () => { ui.closeEditModal() }
  }

  const cancelAddSmall = document.getElementById('cancelAddSmall')
  if (cancelAddSmall !== null) {
    cancelAddSmall.onclick = () => { ui.closeAddModal() }
  }

  const cancelAdd = document.getElementById('cancelAdd')
  if (cancelAdd !== null) {
    cancelAdd.onclick = () => { ui.closeAddModal() }
  }

  const moveButton = document.getElementById('moveButton')
  if (moveButton !== null) {
    moveButton.addEventListener('click', function () {
      ui.toggleMoveMode(false, geodata)
    })
  }

  const cancelMoveButton = document.getElementById('cancelMoveButton')
  if (cancelMoveButton !== null) {
    cancelMoveButton.addEventListener('click', function () {
      ui.toggleMoveMode(true, geodata)
    })
  }

  const addNewCountry = document.getElementById('addCountry')
  if (addNewCountry !== null) {
    addNewCountry.addEventListener('click', function () {
      ui.openAddModal(GEO_TYPES.COUNTRY, geodata)
    })
  }
  const addNewArea = document.getElementById('addArea')
  if (addNewArea !== null) {
    addNewArea.addEventListener('click', function () {
      ui.openAddModal(GEO_TYPES.AREA, geodata)
    })
  }
  const addNewMunicipality = document.getElementById('addMunicipality')
  if (addNewMunicipality !== null) {
    addNewMunicipality.addEventListener('click', function () {
      ui.openAddModal(GEO_TYPES.MUNICIPALITY, geodata)
    })
  }

  const country = document.getElementById('country')
  const newName = document.getElementById('newName') as HTMLInputElement
  const addNewName = document.getElementById('addNewName') as HTMLInputElement
  const section = document.getElementsByClassName('section')[0] as HTMLElement
  section.addEventListener('click', function () {
    ui.selectAndMoveNode(undefined, geodata)
  })

  if (newName !== null) {
    newName.oninput = function (event: Event) {
      const e = event as InputEvent

      if (e.data !== null && !(/^[a-z A-ZåäöÅÄÖ]+$/.test(e.data))) {
        newName.value = newName.value.slice(0, -e.data.length)
      }
    }
  }

  if (addNewName !== null) {
    addNewName.oninput = function (event: Event) {
      const e = event as InputEvent

      if (e.data !== null && !(/^[a-z A-ZåäöÅÄÖ]+$/.test(e.data))) {
        addNewName.value = addNewName.value.slice(0, -e.data.length)
      }
    }
  }
}).catch(console.error)
