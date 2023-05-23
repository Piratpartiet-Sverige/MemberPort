import React from 'react'
import ReactDOM from 'react-dom/client'
import { afterPageLoad } from '../utils/after-page-load'
import CalendarsView from '@memberport/views/calendar/CalendarsView'

let calendarsViewRootEl: HTMLElement | null = null

afterPageLoad().then(() => {
  calendarsViewRootEl = document.getElementById('calendars-view-root')
  if (calendarsViewRootEl !== null) {
    // React calendar root
    ReactDOM
      .createRoot(calendarsViewRootEl)
      .render(React.createElement(CalendarsView, {}))
  }
}).catch(console.error)
