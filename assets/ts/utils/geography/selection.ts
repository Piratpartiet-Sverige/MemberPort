import { GeoData, GEO_TYPES } from './geodata'

const pendingNodes: { [id: string]: HTMLDivElement[] } = {}

export function filter (query: string): void {
  const searchables = document.querySelectorAll('.searchable')

  if (query.length === 0) {
    searchables.forEach(function (searchable: Element) {
      searchable.parentElement?.classList.remove('is-hidden')
    })
    return
  }

  searchables.forEach(function (searchable: Element) {
    const nameElement = searchable.lastChild
    const parentElement = searchable.parentElement

    if (nameElement === null || parentElement === null) {
      return
    }

    const name = nameElement.textContent

    if (name === null) {
      return
    }

    const pattern = new RegExp(query, 'i')

    if (name.search(pattern) !== -1) {
      parentElement.classList.remove('no-border')
      searchable.classList.remove('is-hidden')
    } else {
      parentElement.classList.add('no-border')
      searchable.classList.add('is-hidden')
    }
  })
}

export function addCountry (id: string, name: string, parent: string, geodata: { [id: string]: GeoData }): void {
  const parentElement = document.getElementById(parent)
  const country = createHTML(id, name, 'fa-flag', geodata)
  parentElement?.appendChild(country)
}

export function addArea (id: string, name: string, parent: string, geodata: { [id: string]: GeoData }): void {
  const parentElement = document.getElementById(parent)
  const area = createHTML(id, name, 'fa-layer-group', geodata)

  if (parentElement != null) {
    parentElement.appendChild(area)
    const parentInput = parentElement.querySelector('input') as HTMLInputElement

    if (pendingNodes[id] === null || pendingNodes[id] === undefined) {
      if (parentInput.checked) {
        const input = area.querySelector('.indent input') as HTMLInputElement
        input.checked = true
      }

      return
    }

    pendingNodes[id].forEach(function (node) {
      parentElement.appendChild(node)
    })

    if (parentInput.checked) {
      const children = parentElement.querySelectorAll('.indent input')

      children.forEach(function (child: Element) {
        const childInput = child as HTMLInputElement
        childInput.checked = true
      })
    }
  } else {
    if (pendingNodes[parent] === null || pendingNodes[parent] === undefined) {
      pendingNodes[parent] = []
    }

    pendingNodes[parent].push(area)
  }
}

export function addMunicipality (id: string, name: string, parent: string, geodata: {[id: string]: GeoData}): void {
  const parentElement = document.getElementById(parent)
  const municipality = createHTML(id, name, 'fa-home', geodata)

  if (parentElement != null) {
    parentElement.appendChild(municipality)
    const parentInput = parentElement.querySelector('.indent input') as HTMLInputElement

    if (parentInput?.checked) {
      const query = municipality.querySelector('.indent input') as HTMLInputElement
      query.checked = true
    }
  } else {
    if (pendingNodes[parent] === null || pendingNodes[parent] === undefined) {
      pendingNodes[parent] = []
    }

    pendingNodes[parent].push(municipality)
  }
}

export function getCheckedCountries (parent: string): string {
  const parentElement = document.getElementById(parent)

  if (parentElement === null) {
    return ''
  }

  let countryIDs = ''
  const countries = parentElement.getElementsByClassName('country')

  for (let i = 0; i < countries.length; i++) {
    const country = countries.item(i) as HTMLElement
    const anchorElement = country.firstChild
    const label = anchorElement?.firstChild
    const input = label?.firstChild as HTMLInputElement

    if (input.checked) {
      if (countryIDs.length > 0) {
        countryIDs += ','
      }

      countryIDs += country.id
    }
  }

  return countryIDs
}

export function getCheckedAreas (parent: string): string {
  const parentElement = document.getElementById(parent)

  if (parentElement === null) {
    return ''
  }

  let areaIDs = ''
  const areas = parentElement.getElementsByClassName('area')

  for (let i = 0; i < areas.length; i++) {
    const area = areas.item(i) as HTMLElement
    const parentElement = area.parentElement

    if (parentElement !== null) {
      const input = parentElement.querySelector('input')
      if (input?.checked === true) {
        continue // Only include the top level selection, not all children
      }
    }

    const anchorElement = area.firstChild
    const label = anchorElement?.firstChild
    const input = label?.firstChild as HTMLInputElement

    if (input.checked) {
      if (areaIDs.length > 0) {
        areaIDs += ','
      }

      areaIDs += area.id
    }
  }

  return areaIDs
}

export function getCheckedMunicipalities (parent: string): string {
  const parentElement = document.getElementById(parent)

  if (parentElement === null) {
    return ''
  }

  let municipalityIDs = ''
  const municipalities = parentElement.getElementsByClassName('municipality')

  for (let i = 0; i < municipalities.length; i++) {
    const municipality = municipalities.item(i) as HTMLElement
    const parentElement = municipality.parentElement
    console.log(municipality.id)

    if (parentElement !== null) {
      const input = parentElement.querySelector('input')
      if (input?.checked === true) {
        continue // Only include the top level selection, not all children
      }
    }

    const anchorElement = municipality.firstChild
    const label = anchorElement?.firstChild
    const input = label?.firstChild as HTMLInputElement

    if (input.checked) {
      if (municipalityIDs.length > 0) {
        municipalityIDs += ','
      }

      municipalityIDs += municipality.id
    }
  }

  return municipalityIDs
}

function createHTML (id: string, name: string, icon: string, geodata: {[id: string]: GeoData}): HTMLDivElement {
  const element = document.createElement('div')
  element.id = id

  if (geodata[id].type === GEO_TYPES.COUNTRY) {
    element.classList.add('country')
  } else if (geodata[id].type === GEO_TYPES.AREA) {
    element.classList.add('indent')
    element.classList.add('area')
  } else if (geodata[id].type === GEO_TYPES.MUNICIPALITY) {
    element.classList.add('indent')
    element.classList.add('municipality')
  }

  const anchorElement = document.createElement('a')
  anchorElement.classList.add('panel-block', 'searchable')

  const label = document.createElement('label')
  label.classList.add('checkbox')

  const input = document.createElement('input')
  input.type = 'checkbox'
  label.appendChild(input)

  if (geodata[id]?.active === true) {
    input.checked = true
  }

  input.addEventListener('click', function (event: Event) {
    clickCheck(id, element, input, geodata)
    event.stopPropagation()
  })

  anchorElement.addEventListener('click', function () {
    input.checked = !input.checked
    clickCheck(id, element, input, geodata)
  })

  const span = document.createElement('span')
  span.classList.add('panel-icon')

  const areaIcon = document.createElement('i')
  areaIcon.classList.add('fas')
  areaIcon.classList.add(icon)

  span.appendChild(areaIcon)

  anchorElement.appendChild(label)
  anchorElement.appendChild(span)
  anchorElement.append(name)
  element.appendChild(anchorElement)

  return element
}

function clickCheck (id: string, element: HTMLElement, input: HTMLInputElement, geodata: {[id: string]: GeoData}): void {
  const type = geodata[id].type

  if (type === GEO_TYPES.AREA || type === GEO_TYPES.COUNTRY) {
    const children = element.querySelectorAll('.indent input')

    children.forEach(function (child: Element) {
      const childInput = child as HTMLInputElement
      childInput.checked = input.checked
    })
  }

  if (!input.checked) {
    uncheckTree(element, geodata)
  } else {
    checkTree(element, geodata)
  }
}

function uncheckTree (element: HTMLElement, geodata: {[id: string]: GeoData}): void {
  const query = element.parentElement?.querySelector('.searchable input')
  if (query !== null) {
    const parentInput = query as HTMLInputElement
    parentInput.checked = false
  }

  if (geodata[element.id].type !== GEO_TYPES.COUNTRY && element.parentElement !== null) {
    uncheckTree(element.parentElement, geodata)
  }
}

function checkTree (element: HTMLElement, geodata: {[id: string]: GeoData}): void {
  const children = element.parentElement?.childNodes

  if (children === undefined) {
    return
  }

  let everythingChecked = true

  for (let i = 0; i < children.length; i++) {
    const childElement = children[i] as HTMLElement

    if (childElement.tagName === 'DIV') {
      const anchorElement = childElement.firstChild
      const label = anchorElement?.firstChild
      const input = label?.firstChild as HTMLInputElement

      if (input !== null && input !== undefined && !input.checked) {
        everythingChecked = false
        break
      }
    }
  }

  if (everythingChecked) {
    const query = element.parentElement?.querySelector('.searchable input') as HTMLInputElement
    if (query !== undefined) {
      query.checked = true
    }
  } else {
    return
  }

  if (geodata[element.id].type !== GEO_TYPES.COUNTRY && element.parentElement !== null) {
    checkTree(element.parentElement, geodata)
  }
}
