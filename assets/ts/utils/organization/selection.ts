import type { OrgData } from './orgdata'

const pendingNodes: { [id: string]: HTMLDivElement[] } = {}

export function filter (query: string): void {
  const searchables = document.querySelectorAll('.searchable')

  if (query.length === 0) {
    searchables.forEach(function (searchable: Element) {
      searchable.parentElement?.classList.remove('no-border')
      searchable.classList.remove('is-hidden')
    })

    return
  }

  searchables.forEach(function (searchable: Element) {
    const name = searchable.textContent
    const parentElement = searchable.parentElement

    if (name === null || parentElement === null) {
      return
    }

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

export function addOrganization (id: string, name: string, parent: string, orgdata: { [id: string]: OrgData }, selectable: boolean): void {
  const parentElement = document.getElementById(parent)
  const organization = createHTML(id, name, 'fa-sitemap', orgdata, selectable)

  if (parentElement != null) {
    parentElement.appendChild(organization)
    const parentInput = parentElement.querySelector('input') as HTMLInputElement

    if (pendingNodes[id] === null || pendingNodes[id] === undefined) {
      if (parentInput.checked) {
        const input = organization.querySelector('.indent input') as HTMLInputElement
        input.checked = true
      }

      return
    }

    addPendingNodes(id, organization)

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

    pendingNodes[parent].push(organization)
  }
}

export function getCheckedOrganizations (parent: string): string {
  const parentElement = document.getElementById(parent)

  if (parentElement === null) {
    return ''
  }

  let countryIDs = ''
  const countries = parentElement.getElementsByClassName('organization')

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

function createHTML (id: string, name: string, icon: string, orgdata: { [id: string]: OrgData }, selectable: boolean): HTMLDivElement {
  const element = document.createElement('div')
  element.id = id
  element.classList.add('organization')

  if (orgdata[id].path.includes('.')) {
    element.classList.add('indent')
  }

  const anchorElement = document.createElement('a')
  anchorElement.classList.add('panel-block', 'searchable')

  const label = document.createElement('label')
  label.classList.add('checkbox')

  const input = document.createElement('input')
  input.type = 'checkbox'
  input.disabled = !selectable
  label.appendChild(input)

  if (orgdata[id].active) {
    input.checked = true
  }

  input.addEventListener('click', function (event: Event) {
    if (selectable) {
      clickCheck(id, element, input, orgdata)
    }
    event.stopPropagation()
  })

  anchorElement.addEventListener('click', function () {
    if (selectable) {
      input.checked = !input.checked
      clickCheck(id, element, input, orgdata)
    }
  })

  const span = document.createElement('span')
  span.classList.add('panel-icon')

  const orgIcon = document.createElement('i')
  orgIcon.classList.add('fas')
  orgIcon.classList.add(icon)

  span.appendChild(orgIcon)

  anchorElement.appendChild(label)
  anchorElement.appendChild(span)
  anchorElement.append(name)

  const minimizeExpand = createMinimizeExpand(id)
  anchorElement.append(minimizeExpand)

  element.appendChild(anchorElement)

  return element
}

function createMinimizeExpand (id: string): HTMLDivElement {
  const minimizeExpand = document.createElement('div')
  minimizeExpand.classList.add('is-flex', 'is-flex-grow-1', 'is-justify-content-flex-end', 'is-align-items-center', 'is-align-self-stretch')

  const spanMinimize = document.createElement('span')
  spanMinimize.classList.add('is-align-self-stretch')
  spanMinimize.style.minWidth = '32px'
  spanMinimize.style.height = '100%'
  spanMinimize.onclick = (ev: MouseEvent) => {
    ev.stopPropagation()
    const element = document.getElementById(id)
    const icon = spanMinimize.children.item(0)

    if (icon === null) {
      return
    }

    const hideElements = icon.classList.contains('fa-angle-down')
    if (hideElements) {
      icon.classList.remove('fa-angle-down')
      icon.classList.add('fa-angle-up')
    } else {
      icon.classList.remove('fa-angle-up')
      icon.classList.add('fa-angle-down')
    }

    if (element !== null) {
      const searchables = element.querySelectorAll('.searchable')
      searchables.forEach((searchable: Element) => {
        if (searchable.parentElement?.id === id) {
          return
        }

        if (hideElements) {
          searchable.parentElement?.classList.add('no-border')
          searchable.classList.add('is-hidden')
        } else {
          searchable.parentElement?.classList.remove('no-border')
          searchable.classList.remove('is-hidden')
        }
      })
    }
  }

  const arrowIcon = document.createElement('i')
  arrowIcon.classList.add('fas')
  arrowIcon.classList.add('fa-angle-down')

  spanMinimize.appendChild(arrowIcon)
  minimizeExpand.appendChild(spanMinimize)
  return minimizeExpand
}

function clickCheck (id: string, element: HTMLElement, input: HTMLInputElement, orgdata: { [id: string]: OrgData }): void {
  const children = element.querySelectorAll('.indent input')

  children.forEach(function (child: Element) {
    const childInput = child as HTMLInputElement
    childInput.checked = input.checked
  })

  if (!input.checked) {
    uncheckTree(element, orgdata)
  } else {
    checkTree(element, orgdata)
  }
}

function uncheckTree (element: HTMLElement, orgdata: { [id: string]: OrgData }): void {
  const query = element.parentElement?.querySelector('.searchable input')
  if (query !== null) {
    const parentInput = query as HTMLInputElement
    parentInput.checked = false
  }

  if (orgdata[element.id].path.includes('.') && element.parentElement !== null) {
    uncheckTree(element.parentElement, orgdata)
  }
}

function checkTree (element: HTMLElement, orgdata: { [id: string]: OrgData }): void {
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

  if (orgdata[element.id].path.includes('.') && element.parentElement !== null) {
    checkTree(element.parentElement, orgdata)
  }
}
