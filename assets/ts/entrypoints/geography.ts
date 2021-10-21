import '../../sass/geography.scss'
import { sendUpdateCountryDataRequest, sendUpdateAreaDataRequest, sendUpdateMunicipalityDataRequest, sendDeleteCountryRequest, sendDeleteAreaRequest, sendDeleteMunicipalityRequest } from './api'
import { afterPageLoad } from '../utils/after-page-load'

class GeoData {
  id: string
  name: string
  type: GEO_TYPES
  path: string | undefined
  area: string | undefined

  constructor (id: string, name: string, type: GEO_TYPES, path: string | undefined, area: string | undefined) {
    this.id = id
    this.name = name
    this.type = type
    this.path = path
    this.area = area
  }
}

declare let geodata: { [id: string]: GeoData }
declare let selectedCountryID: string

let selectedNode: HTMLDivElement | undefined
let moveMode = false

enum GEO_TYPES {
  COUNTRY = 'COUNTRY',
  AREA = 'AREA',
  MUNICIPALITY = 'MUNICIPALITY',
}

function renameCountry (id: string, newName: string): void {
  sendUpdateCountryDataRequest(id, newName)
    .then(async (response: Response) => {
      return await response.json()
    })
    .then((data: { [name: string]: any }) => {
      if (data.success === false) {
        throw new Error(data.reason)
      } else if (!changeNodeName(id, newName)) {
        throw new Error('NODE NOT FOUND')
      }

      createMessage('Ändrat namn på landet till: ' + newName, 'is-success')
    }).catch((error: string) => {
      console.error('Error:', error)
      createMessage('Någonting gick fel när namnet på landet skulle uppdateras', 'is-danger')
    })
}

function renameArea (id: string, newName: string): void {
  sendUpdateAreaDataRequest(id, newName, null, null)
    .then(async function (response: Response) {
      return await response.json()
    })
    .then(function (data: { [name: string]: any }) {
      if (data.success === false) {
        throw new Error(data.reason)
      } else if (!changeNodeName(id, newName)) {
        throw new Error('NODE NOT FOUND')
      }

      createMessage('Ändrat namn på området till: ' + newName, 'is-success')
    }).catch((error: string) => {
      console.error('Error:', error)
      createMessage('Någonting gick fel när namnet på området skulle uppdateras', 'is-danger')
    })
}

function renameMunicipality (id: string, newName: string): void {
  sendUpdateMunicipalityDataRequest(id, newName, null, null)
    .then(async function (response: Response) {
      return await response.json()
    })
    .then(function (data: { [name: string]: any }) {
      if (data.success === false) {
        throw new Error(data.reason)
      } else if (!changeNodeName(id, newName)) {
        throw new Error('NODE NOT FOUND')
      }

      createMessage('Ändrat namn på kommunen till: ' + newName, 'is-success')
    }).catch((error: string) => {
      console.error('Error:', error)
      createMessage('Någonting gick fel när namnet på kommunen skulle uppdateras', 'is-danger')
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

function createMessage (message: string, type: string): void {
  const tree = document.getElementById('tree')
  const messageDiv = document.createElement('div')
  messageDiv.classList.add('notification')
  messageDiv.classList.add(type)

  const button = document.createElement('button')
  button.type = 'button'
  button.classList.add('delete')
  button.onclick = () => { messageDiv.remove() }

  const text = document.createElement('p')
  text.textContent = message

  messageDiv.appendChild(button)
  messageDiv.appendChild(text)

  if (tree !== null) {
    tree.insertAdjacentElement('beforebegin', messageDiv)
  }
}

function addArea (id: string, name: string, parent: string): void {
  const parentElement = document.getElementById(parent)
  const area = createArea(id, name, 'fa-layer-group')

  if (parentElement != null) {
    parentElement.appendChild(area)
  }
}

function addMunicipality (id: string, name: string, parent: string): void {
  const parentElement = document.getElementById(parent)
  const municipality = createArea(id, name, 'fa-home')

  if (parentElement != null) {
    parentElement.appendChild(municipality)
  }
}

function addCountry (id: string, name: string): void {
  const tree = document.getElementById('tree')
  const country = createArea(id, name, 'fa-flag')
  country.classList.add('country')

  if (tree != null) {
    tree.appendChild(country)
  }
}

function createArea (id: string, name: string, icon: string): HTMLDivElement {
  const area = document.createElement('div')
  area.id = id

  area.classList.add('node')

  const nameBox = createNameBox(id, name, icon)

  nameBox.addEventListener('click', function (event: Event) {
    selectAndMoveNode(this)
    event.stopPropagation()
  })

  area.appendChild(nameBox)

  return area
}

function createNameBox (id: string, name: string, icon: string): HTMLDivElement {
  const nameBox = document.createElement('div')
  nameBox.classList.add('box')

  const article = document.createElement('article')
  article.classList.add('media')

  const divLeft = document.createElement('div')
  divLeft.classList.add('media-left')

  const areaIconContainer = document.createElement('span')
  areaIconContainer.classList.add('icon')

  const areaIcon = document.createElement('i')
  areaIcon.classList.add('fas')
  areaIcon.classList.add(icon)

  const divMediaContent = document.createElement('div')
  divMediaContent.classList.add('media-content')

  const divContent = document.createElement('div')
  divContent.classList.add('content')
  divContent.textContent = name

  const divRight = document.createElement('div')
  divLeft.classList.add('media-right')

  const editPen = document.createElement('a')
  editPen.classList.add('editPen')
  editPen.onclick = () => { openEditModal(id) }

  const editPenIconContainer = document.createElement('span')
  editPenIconContainer.classList.add('icon')

  const editPenIcon = document.createElement('i')
  editPenIcon.classList.add('fas')
  editPenIcon.classList.add('fa-pen')

  const minimizeExpand = document.createElement('a')
  minimizeExpand.onclick = () => { shrinkList(id) }

  const arrowIconContainer = document.createElement('span')
  arrowIconContainer.classList.add('icon')

  const arrowIcon = document.createElement('i')
  arrowIcon.classList.add('fas')
  arrowIcon.classList.add('fa-angle-up')

  const filler = document.createElement('span')
  filler.style.display = 'inline-block'
  filler.style.width = '1rem'

  const deleteButton = document.createElement('button')
  deleteButton.classList.add('delete')
  deleteButton.onclick = () => { openDeleteModal(id) }

  areaIconContainer.appendChild(areaIcon)
  divLeft.appendChild(areaIcon)

  divMediaContent.appendChild(divContent)

  editPenIconContainer.appendChild(editPenIcon)
  editPen.appendChild(editPenIconContainer)

  arrowIconContainer.appendChild(arrowIcon)
  minimizeExpand.appendChild(arrowIconContainer)

  divRight.appendChild(editPen)
  divRight.appendChild(minimizeExpand)
  divRight.appendChild(filler)
  divRight.appendChild(deleteButton)

  article.appendChild(divLeft)
  article.appendChild(divMediaContent)
  article.appendChild(divRight)

  nameBox.appendChild(article)
  return nameBox
}

function selectAndMoveNode (target: HTMLDivElement | undefined): void {
  if (selectedNode === target) {
    return
  }

  if (selectedNode !== undefined) {
    selectedNode.classList.remove('selected')
  }

  if (target === undefined) {
    selectedNode = undefined
  }

  if (!moveMode) {
    selectedNode = undefined
    return
  }

  if (target !== undefined && selectedNode === undefined) {
    const targetParent = target.parentElement as HTMLElement

    if (geodata[targetParent.id].type !== GEO_TYPES.COUNTRY) {
      selectedNode = target
      selectedNode.classList.add('selected')
    }
  } else if (target !== undefined && selectedNode !== undefined) {
    const newParent = target.parentElement as HTMLElement
    const selectedArea = selectedNode.parentElement as HTMLElement

    if ((geodata[newParent.id].type === GEO_TYPES.AREA || geodata[newParent.id].type === GEO_TYPES.COUNTRY) && selectedArea.parentElement !== newParent) {
      if (geodata[selectedArea.id].type === GEO_TYPES.AREA) {
        moveArea(selectedArea, newParent)
      } else {
        moveMunicipality(selectedArea, newParent)
      }

      selectedNode = undefined
    } else if (geodata[newParent.id].type === GEO_TYPES.COUNTRY) {
      selectedNode.classList.add('selected')
    } else {
      selectedNode = target
      selectedNode.classList.add('selected')
    }
  }
}

function moveArea (area: HTMLElement, parent: HTMLElement): void {
  const children = area.getElementsByClassName('node')
  const path = geodata[area.id].path as string

  for (let index = 0; index < children.length; index++) {
    const child = children.item(index) as Element

    /* Don't allow area to be moved to an area under it */
    if (child.id === parent.id) {
      return
    }
  }

  if (geodata[parent.id].type === GEO_TYPES.MUNICIPALITY) {
    return
  } else if (geodata[parent.id].type === GEO_TYPES.COUNTRY) {
    /* No need to update if the current path is already on the top-level */
    if (path === area.id) {
      return
    }

    /* Update all child nodes */
    for (let index = 0; index < children.length; index++) {
      const child = children.item(index) as Element

      if (geodata[child.id].type === GEO_TYPES.MUNICIPALITY || geodata[child.id].path === undefined) {
        continue
      }

      const childPath = geodata[child.id].path?.slice(path.length + 1) as string
      geodata[child.id].path = area.id + '.' + childPath
      console.log(geodata[child.id].path)
    }

    geodata[area.id].path = area.id
  } else if (geodata[parent.id].type === GEO_TYPES.AREA) {
    const parentPath = geodata[parent.id].path as string
    const newPath = parentPath + '.' + area.id

    /* Update all child nodes */
    for (let index = 0; index < children.length; index++) {
      const child = children.item(index) as Element

      if (geodata[child.id].type === GEO_TYPES.MUNICIPALITY) {
        continue
      }

      const childPath = geodata[child.id].path?.slice(path.length + 1) as string
      geodata[child.id].path = newPath + '.' + childPath
      console.log(geodata[child.id].path)
    }

    geodata[area.id].path = newPath
  }

  parent.appendChild(area)
}

function moveMunicipality (municipality: HTMLElement, parent: HTMLElement): void {
  if (geodata[parent.id].type === GEO_TYPES.MUNICIPALITY) {
    return
  } else if (geodata[parent.id].type === GEO_TYPES.COUNTRY) {
    geodata[municipality.id].area = undefined
  } else if (geodata[parent.id].type === GEO_TYPES.AREA) {
    geodata[municipality.id].area = parent.id
  }

  parent.appendChild(municipality)
}

function expandList (id: string): void {
  if (moveMode) {
    return
  }

  const root = document.getElementById(id)

  if (root === null) {
    return
  }

  const children = root.childNodes

  for (let i = 0; i < children.length; i++) {
    const node = children[i] as HTMLElement
    if (node.classList.contains('node')) {
      node.style.display = ''
    }
  }

  const icon = root.getElementsByClassName('fa-angle-down')[0]

  if (icon !== undefined) {
    icon.classList.remove('fa-angle-down')
    icon.classList.add('fa-angle-up')

    if (icon.parentElement !== null) {
      const button = icon.parentElement.parentElement

      if (button !== null) {
        button.onclick = () => { shrinkList(id) }
      }
    }
  }
}

function shrinkList (id: string): void {
  if (moveMode) {
    return
  }

  const root = document.getElementById(id)

  if (root === null) {
    return
  }

  const children = root.childNodes

  for (let i = 0; i < children.length; i++) {
    const node = children[i] as HTMLElement
    if (node.classList.contains('node')) {
      node.style.display = 'none'
    }
  }

  const icon = root.getElementsByClassName('fa-angle-up')[0]

  if (icon !== undefined) {
    icon.classList.remove('fa-angle-up')
    icon.classList.add('fa-angle-down')

    if (icon.parentElement !== null) {
      const button = icon.parentElement.parentElement

      if (button !== null) {
        button.onclick = () => { expandList(id) }
      }
    }
  }
}

function sendDeleteNodeRequest (id: string): void {
  const nodeType = getNodeType(id)
  const name = geodata[id].name

  if (nodeType === GEO_TYPES.COUNTRY) {
    deleteCountry(id, name)
  } else if (nodeType === GEO_TYPES.AREA) {
    deleteArea(id, name)
  } else if (nodeType === GEO_TYPES.MUNICIPALITY) {
    deleteMunicipality(id, name)
  }
}

function deleteNode (id: string): boolean {
  const node = document.getElementById(id)

  if (node !== null) {
    node.remove()
    return true
  }

  return false
}

function closeDeleteModal (): void {
  const deleteModal = document.getElementById('deleteModal')

  if (deleteModal !== null) {
    deleteModal.classList.remove('is-active')
  }
}

function openDeleteModal (id: string): void {
  const deleteModal = document.getElementById('deleteModal')
  if (deleteModal !== null) {
    deleteModal.classList.add('is-active')
  }

  const deleteText = document.getElementById('deleteText')
  if (deleteText !== null) {
    deleteText.innerText = 'Är du säker på att du vill ta bort ' + geodata[id].name + ' och alla områden och kommuner som tillhör det? Detta går inte att ångra!'
  }

  const deleteNodeButton = document.getElementById('deleteNodeButton')
  if (deleteNodeButton !== null) {
    deleteNodeButton.onclick = () => { sendDeleteNodeRequest(id); closeDeleteModal() }
  }
}

function closeEditModal (): void {
  const editModal = document.getElementById('editModal')

  if (editModal !== null) {
    editModal.classList.remove('is-active')
  }
}

function openEditModal (id: string): void {
  const editModal = document.getElementById('editModal')
  if (editModal !== null) {
    editModal.classList.add('is-active')
  }

  const editNameButton = document.getElementById('editNameButton')
  if (editNameButton !== null) {
    editNameButton.onclick = () => { sendChangeNameRequest(geodata[id].id); closeEditModal() }
  }

  const newNameInput = document.getElementById('newName') as HTMLInputElement
  if (newNameInput !== null) {
    newNameInput.value = geodata[id].name
  }
}

function sendChangeNameRequest (id: string): void {
  const node = document.getElementById(id)
  const newNameInput = document.getElementById('newName') as HTMLInputElement

  if (node === null || newNameInput === null) {
    return
  }

  const newName = newNameInput.value

  const nodeType = getNodeType(id)
  geodata[id].name = newName

  if (nodeType === GEO_TYPES.COUNTRY) {
    renameCountry(id, newName)
  } else if (nodeType === GEO_TYPES.AREA) {
    renameArea(id, newName)
  } else if (nodeType === GEO_TYPES.MUNICIPALITY) {
    renameMunicipality(id, newName)
  }
}

function changeNodeName (id: string, newName: string): boolean {
  const node = document.getElementById(id)

  if (node === null) {
    return false
  }

  geodata[id].name = newName
  const nameBox = node.getElementsByClassName('content')[0] as HTMLElement
  nameBox.innerText = newName
  return true
}

function getNodeType (id: string): GEO_TYPES {
  if (geodata[id].path !== undefined) {
    return GEO_TYPES.AREA
  } else if (geodata[id].area !== undefined) {
    return GEO_TYPES.MUNICIPALITY
  } else {
    return GEO_TYPES.COUNTRY
  }
}

function getParentID (id: string, path: string, fallbackID: string): string {
  let parentID = ''

  if (path === id) {
    parentID = fallbackID
  } else {
    const count = (path.match(/./g) ?? []).length
    if (count === 1) {
      parentID = path.substring(0, path.indexOf('.'))
    } else {
      parentID = path.substring(path.lastIndexOf('.', path.lastIndexOf('.') - 1), path.lastIndexOf('.'))
    }
  }

  return parentID
}

function toggleMoveMode (cancel: boolean): void {
  if (cancel) {
    location.reload()
  }

  const tree = document.getElementById('tree') as HTMLElement
  const moveButton = document.getElementById('moveButton') as HTMLButtonElement
  const cancelMoveButton = document.getElementById('cancelMoveButton') as HTMLButtonElement

  if (moveMode) {
    moveButton.classList.remove('is-success')
    tree.classList.remove('warning')
    selectAndMoveNode(undefined)
    moveButton.classList.add('is-link')

    const text = moveButton.children[1] as HTMLSpanElement
    text.textContent = 'Flytta runt områden'

    cancelMoveButton.style.display = 'none'
  } else {
    moveButton.classList.remove('is-link')
    tree.classList.add('warning')
    moveButton.classList.add('is-success')

    const text = moveButton.children[1] as HTMLSpanElement
    text.textContent = 'Bekräfta flytt'

    cancelMoveButton.style.display = ''
  }

  moveMode = !moveMode
}

afterPageLoad().then(() => {
  addCountry(selectedCountryID, geodata[selectedCountryID].name)
  let parentID = ''

  for (const id in geodata) {
    const data = geodata[id]

    // Check if this is an area
    if (data.type === GEO_TYPES.AREA && data.path !== undefined) {
      parentID = getParentID(data.id, data.path, selectedCountryID)
      addArea(data.id, data.name, parentID)
    } else if (data.type === GEO_TYPES.MUNICIPALITY && data.area !== undefined) { // Municipality
      parentID = data.area

      if (parentID === '') {
        parentID = selectedCountryID
      }

      addMunicipality(data.id, data.name, parentID)
    }
  }

  const cancelDeleteSmall = document.getElementById('cancelDeleteSmall')
  if (cancelDeleteSmall !== null) {
    cancelDeleteSmall.onclick = () => { closeDeleteModal() }
  }

  const cancelDelete = document.getElementById('cancelDelete')
  if (cancelDelete !== null) {
    cancelDelete.onclick = () => { closeDeleteModal() }
  }

  const cancelEditSmall = document.getElementById('cancelEditSmall')
  if (cancelEditSmall !== null) {
    cancelEditSmall.onclick = () => { closeEditModal() }
  }

  const cancelEdit = document.getElementById('cancelEdit')
  if (cancelEdit !== null) {
    cancelEdit.onclick = () => { closeEditModal() }
  }

  const moveButton = document.getElementById('moveButton')
  if (moveButton !== null) {
    moveButton.addEventListener('click', function () {
      toggleMoveMode(false)
    })
  }

  const cancelMoveButton = document.getElementById('cancelMoveButton')
  if (cancelMoveButton !== null) {
    cancelMoveButton.addEventListener('click', function () {
      toggleMoveMode(true)
    })
  }

  const country = document.getElementById('country')
  const newName = document.getElementById('newName') as HTMLInputElement
  const section = document.getElementsByClassName('section')[0] as HTMLElement
  section.addEventListener('click', function () {
    selectAndMoveNode(undefined)
  })

  if (newName !== null) {
    newName.oninput = function (event: Event) {
      const e = event as InputEvent

      if (e.data !== null && !(/^[a-z A-ZåäöÅÄÖ]+$/.test(e.data))) {
        newName.value = newName.value.slice(0, -e.data.length)
      }
    }
  }
}).catch(console.error)
