import { Grid, GridOptions, ModuleRegistry } from '@ag-grid-community/core'
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model'
import { afterPageLoad } from '../utils/after-page-load'

ModuleRegistry.register(ClientSideRowModelModule)

declare const _GRID_DATA_: Array<{
  number: string
  name: string
  email: string
  phone: string
  birthday: string
  postalCode: string
  city: string
  street: string
  country: string
}>

const defaultColDef = {
  sortable: true,
  resizable: true
}

// specify the columns
const columnDefs = [
  { headerName: '#', field: 'number' },
  { headerName: 'Namn', field: 'name' },
  { headerName: 'E-mail', field: 'email' },
  { headerName: 'Telefon', field: 'phone' },
  { headerName: 'Födelsedag', field: 'birthday' },
  { headerName: 'Postkod', field: 'postalCode' },
  { headerName: 'Postort', field: 'city' },
  { headerName: 'Adress', field: 'street' },
  { headerName: 'Land', field: 'country' }
]

// let the grid know which columns and what data to use
const gridOptions: GridOptions = {
  columnDefs,
  defaultColDef,
  rowData: _GRID_DATA_,
  domLayout: 'autoHeight',
  onFirstDataRendered (event) {
    const allColumnIds: string[] = []
    const columns = event.columnApi.getColumns()

    if (columns == null) {
      event.api.sizeColumnsToFit()
      return
    }

    columns.forEach((column) => {
      allColumnIds.push(column.getId())
    })

    event.columnApi.autoSizeColumns(allColumnIds, false)
  }
}

afterPageLoad().then(() => {
  const eGridDiv = document.querySelector<HTMLElement>('#myGrid')

  if (eGridDiv != null) {
    // eslint-disable-next-line no-new
    new Grid(eGridDiv, gridOptions)
  }
}).catch(console.error)
