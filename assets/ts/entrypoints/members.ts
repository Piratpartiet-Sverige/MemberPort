import { Grid, GridOptions, ModuleRegistry } from '@ag-grid-community/all-modules'
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model'
import { afterPageLoad } from '../utils/after-page-load'

ModuleRegistry.register(ClientSideRowModelModule)

declare const _GRID_DATA_: Array<{
  number: string
  name: string
  email: string
  phone: string
  postalCode: string
  city: string
  street: string
  country: string
}>

// specify the columns
const columnDefs = [
  { headerName: 'Medlemsnummer', field: 'number' },
  { headerName: 'Namn', field: 'name' },
  { headerName: 'E-mail', field: 'email' },
  { headerName: 'Telefon', field: 'phone' },
  { headerName: 'Postkod', field: 'postalCode' },
  { headerName: 'Stad', field: 'city' },
  { headerName: 'Adress', field: 'street' },
  { headerName: 'Land', field: 'country' }
]

// let the grid know which columns and what data to use
const gridOptions: GridOptions = {
  columnDefs: columnDefs,
  rowData: _GRID_DATA_
}

afterPageLoad().then(() => {
  // lookup the container we want the Grid to use
  const eGridDiv = document.querySelector<HTMLElement>('#myGrid')
  // create the grid passing in the div to use together with the columns & data we want to use
  if (eGridDiv != null) {
    // eslint-disable-next-line no-new
    new Grid(eGridDiv, gridOptions)
  }
}).catch(console.error)
