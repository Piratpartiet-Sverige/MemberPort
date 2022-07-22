import { sendCreateCalendarRequest, sendUpdateCalendarRequest, sendDeleteCalendarRequest } from '../utils/api'
import { createMessage } from '../utils/ui'
import { Grid, GridOptions, ModuleRegistry } from '@ag-grid-community/core'
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model'
import { afterPageLoad } from '../utils/after-page-load'
import { ButtonRenderer } from '../ag-components/button-renderer'

ModuleRegistry.register(ClientSideRowModelModule)

declare const _GRID_DATA_: Array<{
  id: string
  description: string
  url: string
}>

const defaultColDef = {
  sortable: true,
  resizable: true,
  editable: true
}

const columnDefs = [
  { headerName: 'Beskrivning', field: 'description' },
  { headerName: 'URL', field: 'url' },
  { headerName: 'Ta bort', field: 'delete', cellRenderer: 'buttonRenderer', editable: false, sortable: false, suppressSizeToFit: true }
]

const rowData = _GRID_DATA_.map((row) => ({
  ...row,
  delete: {
    style: 'is-danger',
    label: 'Ta bort',
    onClick: () => { deleteButton(row.id, row.description) }
  }
}))

function deleteButton (rowID: string, description: string): void {
  const result = confirm(`Är du säker på att du vill ta bort ${description}?`)
  if (result) {
    sendDeleteCalendarRequest(rowID)
      .then(response => {
        if (response.status === 204) {
          const transaction = {
            remove: [{ id: rowID }]
          }

          gridOptions.api?.applyTransaction(transaction)
          createMessage('Kalender: ' + description + ' är borttagen', 'is-success', 'calendars')
        } else {
          createMessage('Något gick fel när kalendern skulle tas bort', 'is-danger', 'calendars')
        }
      })
      .catch(console.error)
  }
}

// let the grid know which columns and what data to use
const gridOptions: GridOptions = {
  getRowId: (params) => params.data.id,
  columnDefs,
  defaultColDef,
  rowData,
  components: {
    buttonRenderer: ButtonRenderer
  },
  domLayout: 'autoHeight',
  editType: 'fullRow',
  onFirstDataRendered (event) {
    event.api.sizeColumnsToFit()
  },
  onRowValueChanged: event => {
    if (event.node.id?.startsWith('temp') === true) {
      sendCreateCalendarRequest(event.data.description, event.data.url)
        .then(async function (response: Response) {
          if (response.status === 400) {
            createMessage('Beskrivning eller URL saknades när kalender skulle skapas', 'is-danger', 'calendars')
            throw new Error(response.statusText)
          }

          return await response.json()
        }).then(function (data: { [name: string]: any }) {
          if (data.success === true) {
            const description = data.data.description as string
            createMessage('Ny kalender skapad: ' + description, 'is-success', 'calendars')

            event.node.setId(data.data.id)
            event.node.setDataValue('delete', {
              style: 'is-danger',
              label: 'Ta bort',
              onClick: () => { deleteButton(data.data.id, description) }
            })
          } else {
            createMessage('Något gick fel när kalendern skulle skapas', 'is-danger', 'calendars')
          }
        }).catch(console.error)
    } else if (event.node.id !== undefined) {
      sendUpdateCalendarRequest(event.node.id, event.data.description, event.data.url)
        .then(async function (response: Response) {
          if (response.status === 400) {
            createMessage('Beskrivning och URL saknades när kalender skulle uppdateras', 'is-danger', 'calendars')
            throw new Error(response.statusText)
          }

          return await response.json()
        }).then(function (data: { [name: string]: any }) {
          if (data.success === true) {
            const description = data.data.description as string
            createMessage('Kalender: ' + description + ' uppdaterad', 'is-success', 'calendars')
          } else {
            createMessage('Något gick fel när kalendern skulle uppdateras', 'is-danger', 'calendars')
          }
        }).catch(console.error)
    }
  }
}

afterPageLoad().then(() => {
  const eGridDiv = document.querySelector<HTMLElement>('#calendars')

  if (eGridDiv != null) {
    // eslint-disable-next-line no-new
    new Grid(eGridDiv, gridOptions)
  }

  const addButton = document.getElementById('addButton')

  if (addButton !== null) {
    addButton.onclick = function () {
      const tempID = 'temp' + Math.random().toString(36).substring(2)

      const transaction = {
        add: [
          {
            id: tempID,
            description: '',
            url: '',
            delete: {
              style: 'is-danger',
              label: 'Ta bort',
              onClick: () => {
                const transaction = {
                  remove: [{ id: tempID }]
                }

                gridOptions.api?.applyTransaction(transaction)
              }
            }
          }
        ]
      }

      const newRow = gridOptions.api?.applyTransaction(transaction)

      if (newRow !== null || newRow !== undefined) {
        newRow?.add.forEach((row) => {
          if (row.rowIndex === null) {
            return
          }

          gridOptions.api?.setFocusedCell(row.rowIndex, 'description')
          gridOptions.api?.startEditingCell({
            rowIndex: row.rowIndex,
            colKey: 'description'
          })
        })
      }
    }
  }
}).catch(console.error)
