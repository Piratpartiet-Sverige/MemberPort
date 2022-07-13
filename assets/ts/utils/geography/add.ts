import { GeoData } from './geodata'
import { selectAndMoveNode, openDeleteModal, openEditModal, shrinkList } from './ui'

const pendingNodes: { [id: string]: HTMLDivElement[] } = {}

export function addArea (id: string, name: string, parent: string, geodata: {[id: string]: GeoData}): void {
  const parentElement = document.getElementById(parent)
  const area = createArea(id, name, 'fa-layer-group', geodata)

  if (parentElement != null) {
    parentElement.appendChild(area)
    addPendingNodes(id, area)
  } else {
    if (pendingNodes[parent] === null || pendingNodes[parent] === undefined) {
      pendingNodes[parent] = []
    }

    pendingNodes[parent].push(area)
  }
}

export function addMunicipality (id: string, name: string, parent: string, geodata: {[id: string]: GeoData}): void {
  const parentElement = document.getElementById(parent)
  const municipality = createArea(id, name, 'fa-home', geodata)

  if (parentElement != null) {
    parentElement.appendChild(municipality)
  } else {
    if (pendingNodes[parent] === null || pendingNodes[parent] === undefined) {
      pendingNodes[parent] = []
    }

    pendingNodes[parent].push(municipality)
  }
}

export function addCountry (id: string, name: string, geodata: {[id: string]: GeoData}): void {
  const tree = document.getElementById('tree')
  const country = createArea(id, name, 'fa-flag', geodata)
  country.classList.add('country')

  if (tree != null) {
    tree.appendChild(country)
  }
}

export async function sendCreateCountryRequest (name: string): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement
  const dataBody = 'name=' + name

  const response = await fetch('/api/geography/country', {
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

export async function sendCreateAreaRequest (name: string, countryID: string): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement
  const dataBody = 'name=' + name + '&country=' + countryID

  const response = await fetch('/api/geography/area', {
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

export async function sendCreateMunicipalityRequest (name: string, countryID: string): Promise<Response> {
  const xsrf = document.getElementsByName('_xsrf')[0] as HTMLInputElement
  const dataBody = 'name=' + name + '&country=' + countryID

  const response = await fetch('/api/geography/municipality', {
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

function addPendingNodes (id: string, parent: HTMLDivElement): void {
  if (pendingNodes[id] === null || pendingNodes[id] === undefined) {
    return
  }

  pendingNodes[id].forEach(function (node) {
    parent.appendChild(node)
    addPendingNodes(node.id, node)
  })

  pendingNodes[id] = []
}

function createArea (id: string, name: string, icon: string, geodata: {[id: string]: GeoData}): HTMLDivElement {
  const area = document.createElement('div')
  area.id = id

  area.classList.add('node')

  const nameBox = createNameBox(id, name, icon, geodata)

  nameBox.addEventListener('click', function (event: Event) {
    selectAndMoveNode(this, geodata)
    event.stopPropagation()
  })

  area.appendChild(nameBox)

  return area
}

function createNameBox (id: string, name: string, icon: string, geodata: {[id: string]: GeoData}): HTMLDivElement {
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
  editPen.onclick = () => { openEditModal(id, geodata) }

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
  deleteButton.onclick = () => { openDeleteModal(id, geodata) }

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
