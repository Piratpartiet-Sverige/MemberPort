import { Grid, GridOptions, ModuleRegistry } from '@ag-grid-community/core'
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model'
import { afterPageLoad } from '../utils/after-page-load'
import { createMessage } from '../utils/ui'
import { filter, addOrganization } from '../utils/organization/selection'
import { ButtonRenderer } from '../ag-components/button-renderer'
import { CheckboxRenderer } from '../ag-components/checkbox-renderer'
import '../../sass/selection.scss'
import type { OrgData } from 'assets/ts/utils/organization/orgdata'

declare let orgdata: { [id: string]: OrgData }

ModuleRegistry.register(ClientSideRowModelModule)

declare const _GRID_DATA_: Array<{
  id: string
  name: string
  description: string
  active: {
    checked: 'true' | 'false'
    disabled: boolean
  }
}>

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

// specify the columns
const columnDefs = [
  { headerName: 'Namn', field: 'name', sortable: true },
  { headerName: 'Beskrivning', field: 'description', sortable: true },
  { headerName: 'Aktiv', field: 'active', cellRenderer: 'checkboxRenderer', suppressSizeToFit: true },
  { headerName: 'Ändra', field: 'edit', cellRenderer: 'buttonRenderer', suppressSizeToFit: true },
  { headerName: 'Ta bort', field: 'delete', cellRenderer: 'buttonRenderer', suppressSizeToFit: true }
]

const rowData = _GRID_DATA_.map((row) => ({
  ...row,
  edit: {
    style: 'is-link',
    label: 'Ändra',
    onClick: () => { window.location.href = `edit-organization?id=${row.id}` }
  },
  delete: {
    style: 'is-danger',
    label: 'Ta bort',
    onClick: () => {
      const result = confirm(`Är du säker på att du vill ta bort ${row.name}? Detta tar även bort ALLA underföreningar som tillhör den`)
      if (result) {
        const details: { [key: string]: string } = {
          _xsrf: document.querySelector<HTMLInputElement>('[name=_xsrf]')?.value ?? ''
        }

        const formBody = Object.keys(details).map(key => encodeURIComponent(key) + '=' + encodeURIComponent(details[key])).join('&')

        fetch(`/api/organization/${row.id}`, {
          method: 'DELETE', // *GET, POST, PUT, DELETE, etc.
          mode: 'cors', // no-cors, *cors, same-origin
          cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
          credentials: 'same-origin', // include, *same-origin, omit
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          redirect: 'follow',
          referrerPolicy: 'no-referrer',
          body: formBody
        })
          .then(response => {
            if (response.status === 204) {
              const removedOrgs = [{ id: row.id }]
              for (const id in orgdata) {
                if (id === row.id) {
                  continue
                } else if (orgdata[id].path.includes(row.id)) {
                  removedOrgs.push({ id: id })
                }
              }

              const transaction = {
                remove: removedOrgs
              }
              gridOptions.api?.applyTransaction(transaction)
              const orgNode = document.getElementById(row.id)

              if (orgNode !== null) {
                orgNode.remove()
              }

              createMessage('Föreningen ' + row.name + ' och dess underföreningar togs bort', 'is-success', 'buttonGroup')
            } else {
              createMessage('Någonting gick fel när föreningen skulle raderas', 'is-danger', 'buttonGroup')
            }
          })
          .catch(console.error)
      }
    }
  }
}))

// let the grid know which columns and what data to use
const gridOptions: GridOptions = {
  getRowId: (params) => params.data.id,
  columnDefs,
  defaultColDef: {
    resizable: true
  },
  rowData,
  components: {
    buttonRenderer: ButtonRenderer,
    checkboxRenderer: CheckboxRenderer
  },
  domLayout: 'autoHeight',
  onFirstDataRendered (event) {
    event.api.sizeColumnsToFit()
  }
}

afterPageLoad().then(() => {
  const eGridDiv = document.querySelector<HTMLElement>('#organizations')

  if (eGridDiv != null) {
    // eslint-disable-next-line no-new
    new Grid(eGridDiv, gridOptions)
  }

  for (const id in orgdata) {
    const data = orgdata[id]
    const parentID = getParentID(data.id, data.path, 'organizationsTree')
    addOrganization(data.id, data.name, parentID, orgdata, false)
  }

  const search = document.getElementById('searchOrganization') as HTMLInputElement
  if (search !== null) {
    search.oninput = function () {
      filter(search.value)
    }
  }
}).catch(console.error)
