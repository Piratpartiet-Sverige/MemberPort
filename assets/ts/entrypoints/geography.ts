import { sendUpdateCountryDataRequest, sendUpdateAreaDataRequest, sendUpdateMunicipalityDataRequest, sendDeleteCountryRequest, sendDeleteAreaRequest, sendDeleteMunicipalityRequest } from './api'
import { afterPageLoad } from '../utils/after-page-load'

class GeoData {
  id: string
  name: string
  path: string | undefined
  area: string | undefined

  constructor (id: string, name: string, path: string | undefined, area: string | undefined) {
    this.id = id
    this.name = name
    this.path = path
    this.area = area
  }
}

declare let geodata: { [id: string]: GeoData }
declare let selectedCountryID: string

enum GEO_TYPES {
  COUNTRY,
  AREA,
  MUNICIPALITY,
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
  const area = createArea(id, name, true, true, 'fa-layer-group')

  if (parentElement != null) {
    parentElement.appendChild(area)
  }
}

function addMunicipality (id: string, name: string, parent: string): void {
  const parentElement = document.getElementById(parent)
  const area = createArea(id, name, false, true, 'fa-home')

  if (parentElement != null) {
    parentElement.appendChild(area)
  }
}

function addCountry (id: string, name: string): void {
  const tree = document.getElementById('tree')
  const country = createArea(id, name, true, false, 'fa-flag')

  if (tree != null) {
    tree.appendChild(country)
  }
}

function createArea (id: string, name: string, hasDropzone: boolean, draggable: boolean, icon: string): HTMLDivElement {
  const area = document.createElement('div')
  area.id = id
  area.draggable = draggable

  if (draggable) {
    area.ondragstart = (event) => { startDrag(event) }
    area.ondragend = (event) => { stopDrag(event) }
  }

  area.classList.add('node')

  const nameBox = createNameBox(id, name, icon)
  area.appendChild(nameBox)

  if (hasDropzone) {
    const dropzone = createDropZone()
    area.appendChild(dropzone)
  }

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

function createDropZone (): HTMLDivElement {
  const dropzone = document.createElement('div')
  dropzone.ondrop = (event) => { onDrop(event) }
  dropzone.ondragover = (event) => { allowDrop(event) }
  dropzone.classList.add('dropzone')
  dropzone.classList.add('is-hidden')
  dropzone.innerHTML = '<span class="icon is-large"><i class="fas fa-plus"></i></span>'

  return dropzone
}

function allowDrop (ev: Event): void {
  ev.preventDefault()
}

function expandList (id: string): void {
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

function startDrag (ev: DragEvent): void {
  if (ev.dataTransfer !== null && ev.target !== null) {
    const targetElement = ev.target as Element
    ev.dataTransfer.setData('text', targetElement.id)
    showDropZones(targetElement)
  }
}

function showDropZones (draggedNode: Element): void {
  const dropzones = document.getElementsByClassName('dropzone')
  for (let i = 0; i < dropzones.length; i++) {
    dropzones[i].classList.remove('is-hidden')
  }

  const childDropzones = draggedNode.getElementsByClassName('dropzone')
  for (let i = 0; i < childDropzones.length; i++) {
    childDropzones[i].classList.add('is-hidden')
  }

  const parent = draggedNode.parentElement

  if (parent !== null) {
    const parentDropzone = parent.getElementsByClassName('dropzone')[0]
    parentDropzone.classList.add('is-hidden')
  }
}

function hideDropZones (): void {
  const elements = document.getElementsByClassName('dropzone')
  for (let i = 0; i < elements.length; i++) {
    elements[i].classList.add('is-hidden')
  }
}

function stopDrag (ev: Event): void {
  hideDropZones()
}

function onDrop (ev: DragEvent): void {
  ev.preventDefault()

  let data = ''

  if (ev.dataTransfer !== null) {
    data = ev.dataTransfer.getData('text')
  }

  const target = ev.target

  if (target !== null) {
    let node = target as HTMLElement

    while (!node.classList.contains('dropzone') && node.parentElement !== null) {
      node = node.parentElement
    }

    const movedNode = document.getElementById(data)

    if (movedNode !== null) {
      node.insertAdjacentElement('afterend', movedNode)
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

afterPageLoad().then(() => {
  addCountry(selectedCountryID, geodata[selectedCountryID].name)
  let parentID = ''

  for (const id in geodata) {
    const data = geodata[id]

    // Check if this is an area
    if (data.path !== undefined) {
      parentID = getParentID(data.id, data.path, selectedCountryID)
      addArea(data.id, data.name, parentID)
    } else if (data.area !== undefined) { // Municipality
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

  const newName = document.getElementById('newName') as HTMLInputElement

  if (newName !== null) {
    newName.oninput = function (event: Event) {
      const e = event as InputEvent

      if (e.data !== null && !(/^[a-zA-ZåäöÅÄÖ]+$/.test(e.data))) {
        newName.value = newName.value.slice(0, -e.data.length)
      }
    }
  }
}).catch(console.error)
