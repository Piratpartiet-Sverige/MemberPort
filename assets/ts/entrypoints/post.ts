import tinymce from 'tinymce'
import { sendCreatePostRequest } from '../utils/api'
import { afterPageLoad } from '../utils/after-page-load'
import { createMessage } from '../utils/ui'

afterPageLoad().then(() => {
  const editor = tinymce.init({
    selector: 'textarea#editor'
  })

  const publish = document.getElementById('publish')
  if (publish !== null) {
    publish.onclick = function () {
      const postTitleElement = document.getElementById('postTitle') as HTMLInputElement
      const postBody = tinymce.activeEditor.getContent()
      let postTitle = ''

      if (postTitleElement !== null) {
        postTitle = postTitleElement.value
      }

      sendCreatePostRequest(postTitle, postBody).then((response: Response) => {
        if (response.ok) {
          createMessage('Inlägget är publicerat!', 'is-success', 'message')
        } else if (response.status === 403) {
          createMessage('Du har inte behörighet att publicera detta inlägg', 'is-danger', 'message')
        } else if (response.status === 422) {
          createMessage('Rubriken eller innehållet får inte vara tomt', 'is-danger', 'message')
        } else if (response.status === 500) {
          createMessage('Något gick fel när inlägget skulle publiceras', 'is-danger', 'message')
        }
      }).catch((reason) => {
        console.log(reason)
        createMessage('Något gick fel när inlägget skulle publiceras', 'is-danger', 'message')
      })
    }
  }
}).catch(console.error)
