export async function afterPageLoad (): Promise<void> {
  return await new Promise<void>((resolve) => {
    if (document.readyState !== 'loading') {
      resolve()
    } else {
      document.addEventListener('DOMContentLoaded', () => {
        resolve()
      })
    }
  })
}
