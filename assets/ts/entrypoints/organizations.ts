import { Grid, GridOptions, ModuleRegistry } from '@ag-grid-community/core'
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model'
import { afterPageLoad } from '../utils/after-page-load'
import { ButtonRenderer } from '../ag-components/button-renderer'
import { CheckboxRenderer } from '../ag-components/checkbox-renderer'

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

// specify the columns
const columnDefs = [
  { headerName: 'Namn', field: 'name', sortable: true },
  { headerName: 'Beskrivning', field: 'description', sortable: true },
  { headerName: 'Aktiv', field: 'active', cellRenderer: 'checkboxRenderer' },
  { headerName: 'Ändra', field: 'edit', cellRenderer: 'buttonRenderer' },
  { headerName: 'Ta bort', field: 'delete', cellRenderer: 'buttonRenderer' }
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
      const result = confirm(`Är du säker på att du vill ta bort ${row.name}`)
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
            if (response.status === 203) { location.reload() }
          })
          .catch(console.error)
      }
    }
  }
}))

// let the grid know which columns and what data to use
const gridOptions: GridOptions = {
  columnDefs: columnDefs,
  rowData: rowData,
  components: {
    buttonRenderer: ButtonRenderer,
    checkboxRenderer: CheckboxRenderer
  }
}

afterPageLoad().then(() => {
  // lookup the container we want the Grid to use
  const eGridDiv = document.querySelector<HTMLElement>('#organizations')
  // create the grid passing in the div to use together with the columns & data we want to use
  if (eGridDiv != null) {
    // eslint-disable-next-line no-new
    new Grid(eGridDiv, gridOptions)
  }
}).catch(console.error)
