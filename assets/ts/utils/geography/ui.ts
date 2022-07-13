import { sendDeleteNodeRequest } from './delete'
import { sendChangeNameRequest } from './edit'
import { sendCreateCountryRequest, sendCreateAreaRequest, sendCreateMunicipalityRequest, addArea, addMunicipality } from './add'
import { GeoData, GEO_TYPES } from './geodata'
import { sendUpdateAreasRequest, sendUpdateMunicipalitiesRequest } from '../api'

export let selectedNode: HTMLDivElement | undefined
export let moveMode = false
export let movedAreas: { [id: string]: GeoData } = {}
export let movedMunicipalities: { [id: string]: GeoData } = {}

export function createMessage (message: string, type: string, parent = 'tree'): void {
  const tree = document.getElementById(parent)
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

export function closeDeleteModal (): void {
  const deleteModal = document.getElementById('deleteModal')

  if (deleteModal !== null) {
    deleteModal.classList.remove('is-active')
  }
}

export function openDeleteModal (id: string, geodata: { [id: string]: GeoData }): void {
  const name = geodata[id].name
  const deleteModal = document.getElementById('deleteModal')
  if (deleteModal !== null) {
    deleteModal.classList.add('is-active')
  }

  const deleteText = document.getElementById('deleteText')
  if (deleteText !== null) {
    deleteText.innerText = 'Är du säker på att du vill ta bort ' + name + ' och alla områden och kommuner som tillhör det? Detta går inte att ångra!'
  }

  const deleteNodeButton = document.getElementById('deleteNodeButton')
  if (deleteNodeButton !== null) {
    deleteNodeButton.onclick = () => { sendDeleteNodeRequest(id, geodata); closeDeleteModal() }
  }
}

export function openEditModal (id: string, geodata: { [id: string]: GeoData }): void {
  const editModal = document.getElementById('editModal')
  if (editModal !== null) {
    editModal.classList.add('is-active')
  }

  const editNameButton = document.getElementById('editNameButton')
  if (editNameButton !== null) {
    editNameButton.onclick = () => { sendChangeNameRequest(id, geodata); closeEditModal() }
  }

  const newNameInput = document.getElementById('newName') as HTMLInputElement
  if (newNameInput !== null) {
    newNameInput.value = geodata[id].name
  }
}

export function closeEditModal (): void {
  const editModal = document.getElementById('editModal')

  if (editModal !== null) {
    editModal.classList.remove('is-active')
  }
}

export function openAddModal (type: GEO_TYPES, geodata: { [id: string]: GeoData }): void {
  const addModal = document.getElementById('addModal')
  const newNameInput = document.getElementById('addNewName') as HTMLInputElement
  const addTitle = document.getElementById('addTitle')
  const addNewButton = document.getElementById('addNewButton')

  if (addModal === null || newNameInput === null || addTitle === null || addNewButton === null) {
    return
  }

  addModal.classList.add('is-active')
  newNameInput.value = ''

  switch (type) {
    case GEO_TYPES.AREA:
      addTitle.textContent = 'Skapa nytt område'
      addNewButton.onclick = () => {
        const countryInput = document.getElementById('country') as HTMLSelectElement
        const newNameInput = document.getElementById('addNewName') as HTMLInputElement

        if (newNameInput !== null) {
          sendCreateAreaRequest(newNameInput.value, countryInput.value)
            .then(async (response: Response) => {
              return await response.json()
            })
            .then((data: { [name: string]: any }) => {
              if (data.success === false) {
                throw new Error(data.reason)
              }
              const dataBody = data.data

              createMessage('Nytt område skapat: ' + (dataBody.name as string), 'is-success')
              geodata[dataBody.id] = new GeoData(dataBody.id, dataBody.name, GEO_TYPES.AREA, dataBody.path, undefined)
              addArea(dataBody.id, dataBody.name, dataBody.country_id, geodata)
            }).catch((error: string) => {
              console.error('Error:', error)
              createMessage('Någonting gick fel när området skulle skapas', 'is-danger')
            })
        }
        closeAddModal()
      }
      break
    case GEO_TYPES.COUNTRY:
      addTitle.textContent = 'Skapa nytt land'
      addNewButton.onclick = () => {
        const newNameInput = document.getElementById('addNewName') as HTMLInputElement
        if (newNameInput !== null) {
          sendCreateCountryRequest(newNameInput.value)
            .then(async (response: Response) => {
              return await response.json()
            })
            .then((data: { [name: string]: any }) => {
              if (data.success === false) {
                throw new Error(data.reason)
              }
              const dataBody = data.data

              createMessage('Nytt land skapat: ' + (dataBody.name as string), 'is-success')
            }).catch((error: string) => {
              console.error('Error:', error)
              createMessage('Någonting gick fel när landet skulle skapas', 'is-danger')
            })
        }
        closeAddModal()
      }
      break
    case GEO_TYPES.MUNICIPALITY:
      addTitle.textContent = 'Skapa ny kommun'
      addNewButton.onclick = () => {
        const countryInput = document.getElementById('country') as HTMLInputElement
        const newNameInput = document.getElementById('addNewName') as HTMLInputElement

        if (newNameInput !== null) {
          sendCreateMunicipalityRequest(newNameInput.value, countryInput.value)
            .then(async (response: Response) => {
              return await response.json()
            })
            .then((data: { [name: string]: any }) => {
              if (data.success === false) {
                throw new Error(data.reason)
              }
              const dataBody = data.data

              createMessage('Ny kommun skapad: ' + (dataBody.name as string), 'is-success')
              geodata[dataBody.id] = new GeoData(dataBody.id, dataBody.name, GEO_TYPES.MUNICIPALITY, undefined, undefined)
              addMunicipality(dataBody.id, dataBody.name, dataBody.country_id, geodata)
            }).catch((error: string) => {
              console.error('Error:', error)
              createMessage('Någonting gick fel när kommunen skulle skapas', 'is-danger')
            })
        }
        closeAddModal()
      }
      break
  }
}

export function closeAddModal (): void {
  const addModal = document.getElementById('addModal')

  if (addModal !== null) {
    addModal.classList.remove('is-active')
  }
}

function moveArea (area: HTMLElement, parent: HTMLElement, geodata: { [id: string]: GeoData }): void {
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

  movedAreas[area.id] = geodata[area.id]
  parent.appendChild(area)
}

function moveMunicipality (municipality: HTMLElement, parent: HTMLElement, geodata: { [id: string]: GeoData }): void {
  if (geodata[parent.id].type === GEO_TYPES.MUNICIPALITY) {
    return
  } else if (geodata[parent.id].type === GEO_TYPES.COUNTRY) {
    geodata[municipality.id].area = undefined
  } else if (geodata[parent.id].type === GEO_TYPES.AREA) {
    geodata[municipality.id].area = parent.id
    movedMunicipalities[municipality.id] = geodata[municipality.id]
  }

  parent.appendChild(municipality)
}

export function selectAndMoveNode (target: HTMLDivElement | undefined, geodata: { [id: string]: GeoData }): void {
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
        moveArea(selectedArea, newParent, geodata)
      } else {
        moveMunicipality(selectedArea, newParent, geodata)
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

export function shrinkList (id: string): void {
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

export function toggleMoveMode (cancel: boolean, geodata: { [id: string]: GeoData }): void {
  if (cancel) {
    location.reload()
    return
  }

  const tree = document.getElementById('tree') as HTMLElement
  const moveButton = document.getElementById('moveButton') as HTMLButtonElement
  const cancelMoveButton = document.getElementById('cancelMoveButton') as HTMLButtonElement

  if (moveMode) {
    moveButton.classList.remove('is-success')
    tree.classList.remove('warning')
    selectAndMoveNode(undefined, geodata)
    moveButton.classList.add('is-link')

    const text = moveButton.children[1] as HTMLSpanElement
    text.textContent = 'Flytta runt områden'

    cancelMoveButton.style.display = 'none'

    if (Object.keys(movedAreas).length > 0) {
      sendUpdateAreasRequest(movedAreas)
        .then(async (response: Response) => {
          return await response.json()
        })
        .then((data: { [name: string]: any }) => {
          if (data.success === false) {
            throw new Error(data.reason)
          }

          createMessage('Flytten av områden gick bra!', 'is-success')
        }).catch((error: string) => {
          console.error('Error:', error)
          createMessage('Någonting gick fel när flytten skulle göras. Vissa områden kan ha flyttat på sig', 'is-danger')
        })
    }

    if (Object.keys(movedMunicipalities).length > 0) {
      sendUpdateMunicipalitiesRequest(movedMunicipalities)
        .then(async (response: Response) => {
          return await response.json()
        })
        .then((data: { [name: string]: any }) => {
          if (data.success === false) {
            throw new Error(data.reason)
          }

          createMessage('Flytten av kommuner gick bra!', 'is-success')
        }).catch((error: string) => {
          console.error('Error:', error)
          createMessage('Någonting gick fel när flytten skulle göras. Vissa kommuner kan ha flyttat på sig', 'is-danger')
        })
    }

    movedAreas = {}
    movedMunicipalities = {}
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
