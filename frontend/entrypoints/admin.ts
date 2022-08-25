import React from 'react'
import ReactDOM from 'react-dom/client'
import { AdminView } from '@memberport/views/admin/AdminView'
import { afterPageLoad } from '../utils/after-page-load'

let adminViewRootEl: HTMLElement | null = null

afterPageLoad().then(() => {
  adminViewRootEl = document.getElementById('admin-view-root')

  if (adminViewRootEl !== null) {
    ReactDOM
      .createRoot(adminViewRootEl)
      .render(React.createElement(AdminView, {}))
  }
}).catch(console.error)
