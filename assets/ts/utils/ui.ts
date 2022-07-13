export function createMessage (message: string, type: string, parent = 'tree'): void {
  const tree = document.getElementById(parent)
  const messageDiv = document.createElement('div')
  messageDiv.classList.add('notification')
  messageDiv.classList.add(type)

  const button = document.createElement('button')
  button.type = 'button'
  button.classList.add('delete')
  button.onclick = () => { messageDiv.remove() }

  const text = document.createElement('p')
  text.textContent = message

  messageDiv.appendChild(button)
  messageDiv.appendChild(text)

  if (tree !== null) {
    tree.insertAdjacentElement('beforebegin', messageDiv)
  }
}
