export function afterPageLoad() {
  return new Promise<void>((resolve) => {
    if (document.readyState !== 'loading') {
      resolve()
    } else {
      document.addEventListener('DOMContentLoaded', () => {
        resolve()
      })
    }
  })
}
