import { updateMunicipalities } from '../utils/api'
import { afterPageLoad } from '../utils/after-page-load'

afterPageLoad().then(() => {
  updateMunicipalities()
  const queryParams = new URLSearchParams(window.location.search)

  const elements = document.getElementsByName('traits.accept_tos')
  if (elements.length > 0) {
    const acceptToS = elements.item(0) as HTMLInputElement
    acceptToS.value = acceptToS.checked.toString()
    acceptToS.onclick = () => { acceptToS.value = acceptToS.checked.toString() }
  }

  const organizationsElement = document.getElementById('organizations')

  if (organizationsElement === null) {
    console.error('Could not find element "organizations"')
    return
  }

  const organizations = organizationsElement as HTMLInputElement

  const orgElements = Array.from(document.getElementsByClassName('organization')) as HTMLElement[]
  orgElements.forEach((element) => {
    const checkOrg = element as HTMLInputElement
    const orgID = checkOrg.getAttribute('org-id') as string

    checkOrg.onclick = () => {
      if (checkOrg.checked) {
        if (organizations.value.length > 0) {
          organizations.value += ','
        }

        organizations.value += orgID
      } else {
        const regExp = new RegExp('^' + orgID + ',?|,?' + orgID, 'g')
        organizations.value = organizations.value.replace(regExp, '')
      }
    }
  })
}).catch(console.error)
