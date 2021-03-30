import { Grid, GridOptions, ModuleRegistry } from '@ag-grid-community/all-modules'
import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model"
import { afterPageLoad } from '../utils/after-page-load'

ModuleRegistry.register(ClientSideRowModelModule);

declare const __GRID_DATA__: any

// specify the columns
const columnDefs = [
  { headerName: "Medlemsnummer", field: "number" },
  { headerName: "Namn", field: "name" },
  { headerName: "E-mail", field: "email" },
  { headerName: "Telefon", field: "phone" },
  { headerName: "Postkod", field: "postal_code" },
  { headerName: "Stad", field: "city" },
  { headerName: "Adress", field: "street" },
  { headerName: "Land", field: "country" },
]

// let the grid know which columns and what data to use
const gridOptions: GridOptions = {
  columnDefs: columnDefs,
  rowData: __GRID_DATA__
}

afterPageLoad().then(() => {
  // lookup the container we want the Grid to use
  const eGridDiv = document.querySelector<HTMLElement>('#myGrid')
  // create the grid passing in the div to use together with the columns & data we want to use
  if (eGridDiv) {
    new Grid(eGridDiv, gridOptions)
  }
})

