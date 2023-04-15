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

  const organizations = document.getElementById('organizations') as HTMLInputElement
  const orgElements = document.getElementsByName('orgIDs')
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
        organizations.value.replace(orgID, '')
      }
    }
  })
}).catch(console.error)
