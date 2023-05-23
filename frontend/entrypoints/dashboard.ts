import { Calendar } from '@fullcalendar/core'
import svLocale from '@fullcalendar/core/locales/sv'
import dayGridPlugin from '@fullcalendar/daygrid'
import iCalendarPlugin from '@fullcalendar/icalendar'
import { afterPageLoad } from '../utils/after-page-load'

afterPageLoad().then(() => {
  const calendarElement = document.getElementById('calendar')

  if (calendarElement !== null) {
    const calendar = new Calendar(calendarElement, {
      events: {
        url: '/api/calendar',
        format: 'ics'
      },
      plugins: [dayGridPlugin, iCalendarPlugin],
      locale: svLocale,
      initialView: 'dayGridMonth',
      headerToolbar: {
        left: 'title',
        center: '',
        right: 'today prev,next'
      }
    })

    calendar.render()
  }
}).catch(console.error)
