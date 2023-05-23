import React from 'react'
import classNames from 'classnames'
import type CalendarItem from './CalendarItem'

interface CalendarTableProps {
  rows: CalendarItem[]
  onEditClick?: (event, id) => any
  id?: string
  className?: string
}

export const CalendarTable: React.FC<CalendarTableProps> = (props) => {
  const {
    rows,
    onEditClick,
    id = 'calendars',
    className
  } = props

  return (
    <table
      id={id}
      className={classNames(
        'table table-calendars is-fullwidth is-striped',
        { 'is-hoverable': rows.length > 0 },
        className
      )}
    >
      <thead>
        <tr>
          <th>Beskrivning</th>
          <th>ICS URL</th>
          <th>Tillagd</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {rows.map(({ id, description, icsUrl, created }) => (
          <tr key={id}>
            <td>{description}</td>
            <td>{icsUrl}</td>
            <td>{created}</td>
            <td className="has-text-right">
              <button
                type="button"
                id="editButton"
                className="button is-warning is-small"
                onClick={onEditClick !== undefined ? (event) => { onEditClick(event, id) } : undefined}
              >Ändra
              </button>
            </td>
          </tr>
        ))}
        {rows.length === 0 &&
          <tr>
            <td colSpan={3}><em>Inga kalendrar hittades</em></td>
          </tr>
        }
      </tbody>
    </table>
  )
}

export default CalendarTable
