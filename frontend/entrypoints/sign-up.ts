import { updateMunicipalities } from '../utils/api'
import { afterPageLoad } from '../utils/after-page-load'

afterPageLoad().then(() => {
  updateMunicipalities()

  const elements = document.getElementsByName('accept_tos')
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
  const transientPayload = {
    organizations: [] as string[]
  }

  const orgElements = Array.from(document.getElementsByClassName('organization')) as HTMLElement[]
  orgElements.forEach((element) => {
    const checkOrg = element as HTMLInputElement
    const orgID = checkOrg.getAttribute('org-id') as string

    checkOrg.onclick = () => {
      if (checkOrg.checked) {
        transientPayload.organizations.push(orgID)
      } else {
        const index = transientPayload.organizations.indexOf(orgID, 0)
        if (index > -1) {
          transientPayload.organizations.splice(index, 1)
        }
      }
      organizations.value = JSON.stringify(transientPayload)
    }
  })
}).catch(console.error)
