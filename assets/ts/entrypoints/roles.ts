import { Grid, GridOptions, ModuleRegistry } from '@ag-grid-community/all-modules'
import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model"
import { afterPageLoad } from '../utils/after-page-load'
import { CheckboxRenderer } from '../ag-components/checkbox-renderer'

ModuleRegistry.register(ClientSideRowModelModule);

declare const __GRID_DATA_COLUMNS__: any
declare const __GRID_DATA_ROWS__: any

// let the grid know which columns and what data to use
const gridOptions: GridOptions = {
  columnDefs: __GRID_DATA_COLUMNS__,
  rowData: __GRID_DATA_ROWS__,
  components: {
      checkboxRenderer: CheckboxRenderer
  }
};

afterPageLoad().then(() => {
  // lookup the container we want the Grid to use

  const saveButton = document.querySelector('#save-roles')

  if (saveButton) {
    saveButton.addEventListener('click', saveRoles)
  }

  const eGridDiv = document.querySelector<HTMLElement>('#myGrid')
  // create the grid passing in the div to use together with the columns & data we want to use
  if (eGridDiv) {
    new Grid(eGridDiv, gridOptions)
  }
})

async function sendRequest() {
  let permissions: Array<string> = [];
  for (let index = 2; index < __GRID_DATA_COLUMNS__.length; index++) {
      permissions.push(__GRID_DATA_COLUMNS__[index].field);
  }

  let rolesData: {[key: string]: any} = {}; 

  gridOptions.api?.forEachNode((node, index) => {
      rolesData[node.data.id] = {};
      for (let i = 0; i < permissions.length; i++) {
          rolesData[node.data.id][permissions[i]] = node.data[permissions[i]];
      }
  });

  const response = await fetch("/admin/roles", {
      method: 'PUT',
      mode: 'cors',
      cache: 'no-cache',
      credentials: 'include',
      headers: {
          'Content-Type': 'application/json',
          'X-XSRFToken': document.querySelector<HTMLInputElement>("[name=_xsrf]")?.value ?? ''
      },
      redirect: 'follow', // manual, *follow, error
      referrerPolicy: 'same-origin',
      body: JSON.stringify(rolesData)
  });

  return response;
}

function show(ID: string) {
  document.getElementById(ID)?.classList.remove('is-hidden');
}

function hide(ID: string) {
  document.getElementById(ID)?.classList.add('is-hidden');
}

function saveRoles() {
  sendRequest()
          .then(response => {
              if (response.ok) {
                  hide("errorNotification");
                  const successElement = document.getElementById("successText");
                  if (successElement) {
                    successElement.innerHTML = "Ändringar sparade";
                  }
                  show("successNotification");
              } else {
                  response.json().then(response => {
                      if (response.error.code >= 400) {
                          hide("successNotification");
                          const errorElement = document.getElementById("errorText");
                          if (errorElement) {
                            errorElement.innerHTML = response.error.message;
                          }
                          show("errorNotification");
                      }
                  });
              }
          });
}