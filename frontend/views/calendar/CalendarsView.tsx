import React, {
  FormEvent,
  SyntheticEvent,
  useEffect,
  useRef,
  useState
} from 'react'
import classNames from 'classnames'
import CalendarTable from './CalendarTable'
import { sendCreateCalendarRequest, sendDeleteCalendarRequest, sendFetchCalendarsRequest, sendUpdateCalendarRequest } from '@memberport/utils/api'
import type CalendarItem from './CalendarItem'

interface CalendarsViewProps {
  id?: string
  className?: string
}

interface FormMessage {
  type: 'success' | 'warning' | 'danger'
  message: string
}

export const CalendarsView: React.FC<CalendarsViewProps> = (props) => {
  const {
    id = 'calendars-view',
    className
  } = props

  const [formMessage, setFormMessage] = useState<FormMessage | null>(null)

  const [editCalendarItem, setEditCalendarItem] = useState<CalendarItem | null>(null)

  const [calendars, setCalendars] = useState<CalendarItem[]>([])

  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  function fetchCalendars (): void {
    sendFetchCalendarsRequest()
      .then(async (response) => {
        const respJson = await response.json()
        setCalendars(respJson.data.map(ci => ({ ...ci, icsUrl: ci.ics_url })) as unknown as CalendarItem[])
      })
      .catch(err => {
        console.warn(err)
      })
  }

  useEffect(() => {
    fetchCalendars()
    return () => {
      if (timeoutRef.current !== null) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  function onCalendarFormSubmit (event: FormEvent): boolean {
    event.preventDefault()
    const data = new FormData(event.target as HTMLFormElement)
    // Client validation?
    if (!(Boolean(data.get('description')) && Boolean(data.get('ics_url')))) {
      setFormMessage({
        type: 'warning',
        message: 'Var snäll fyll i båda fälten.'
      })
      return false
    }
    // api request
    const request = editCalendarItem === null
      ? sendCreateCalendarRequest(
        data.get('description') as string | null,
        data.get('ics_url') as string | null
      )
      : sendUpdateCalendarRequest(
        editCalendarItem.id,
        data.get('description') as string | null,
        data.get('ics_url') as string | null
      )

    request
      .then(async function (response: Response) {
        const data = await response.json()
        if (response.status === 400) {
          if (data.reason === 'INVALID URL') {
            setFormMessage({
              type: 'warning',
              message: 'Felaktigt format på URL.'
            })
          }
          throw new Error(response.statusText)
        }
        return data
      })
      .then(function (data: { [name: string]: any }) {
        if (data.success === true) {
          const description = data.data.description as string
          setFormMessage({
            type: 'success',
            message: (editCalendarItem ? 'Kalender uppdaterades: ' : 'Ny kalender skapad: ') + description
          })
          fetchCalendars()
          // Hide success message in 3 secs
          timeoutRef.current = setTimeout(() => {
            (event.target as HTMLFormElement).reset()
          }, 3000)
        } else {
          setFormMessage({
            type: 'danger',
            message: 'Något gick fel när kalendern skulle ' + (editCalendarItem ? 'uppdateras' : 'skapas')
          })
        }
      }).catch(console.error)

    return false
  }

  function onCalendarFormReset (event: FormEvent): boolean {
    setFormMessage(null)
    setEditCalendarItem(null)
    return true
  }

  function onEditClick (event: SyntheticEvent, id: string): void {
    setEditCalendarItem(calendars.find(cal => cal.id === id) ?? null)
  }

  function onDeleteClick (event: SyntheticEvent): boolean {
    if (editCalendarItem) {
      sendDeleteCalendarRequest(editCalendarItem.id)
        .then(function (response) {
          if (response.statusText === 'CALENDAR DELETED') {
            setEditCalendarItem(null)
            setFormMessage({
              type: 'success',
              message: 'Kalender raderades'
            })
            fetchCalendars()
            // Hide success message in 3 secs
            timeoutRef.current = setTimeout(() => {
              setFormMessage(null)
            }, 3000)
          }
        })
        .catch(console.error)
    }
    return false
  }

  return (
    <div
      id={id}
      className={classNames('section', className)}
    >
      <div className="container">

        <div className="columns">

          <div className="column is-two-thirds mb-6">
            <h1 className="title">Mina kalendrar</h1>
            <CalendarTable
              rows={calendars}
              onEditClick={onEditClick}
            />
          </div>

          <div className="column">
            <form
              id="calendarForm"
              onSubmit={onCalendarFormSubmit}
              onReset={onCalendarFormReset}
            >
              <fieldset className="box fieldset">
                <legend>{editCalendarItem === null ? 'Lägg till ny' : 'Ändra'}</legend>
                <div className="field">
                  <label
                    className="label"
                    htmlFor="description"
                  >
                    Beskrivning
                  </label>
                  <div className="control">
                    <input
                      className="input"
                      type="text"
                      name="description"
                      defaultValue={editCalendarItem?.description}
                      placeholder="Min piratkalender"
                    />
                  </div>
                </div>
                <div className="field">
                  <label
                    className="label"
                    htmlFor="ics_url"
                  >
                    ICS URL
                  </label>
                  <div className="control">
                    <input
                      className="input"
                      type="text"
                      name="ics_url"
                      defaultValue={editCalendarItem?.icsUrl}
                      placeholder="https://www.ics-adr..."
                    />
                  </div>
                </div>

                {formMessage !== null &&
                  <div className={classNames('notification', `is-${formMessage.type}`, 'p-2')}>
                    {formMessage.message}
                  </div>
                }

                <hr className="my-4" />
                <div className="field is-grouped">
                  <div className="control">
                    <button type="submit" className="button is-primary">Spara</button>
                  </div>
                  <div className="control">
                    <button type="reset" className="button is-primary is-light">Avbryt</button>
                  </div>
                  <div className="is-flex-grow-1" />
                  {editCalendarItem &&
                    <div className="control">
                      <button type="button" className="button is-danger" onClick={onDeleteClick}>Radera</button>
                    </div>
                  }
                </div>
              </fieldset>
            </form>
          </div>

        </div>
      </div>
    </div>
  )
}

export default CalendarsView
