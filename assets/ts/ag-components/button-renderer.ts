import { Component } from '@ag-grid-community/core'

/*
 * Renders buttons in an ag-grid
 */
class ButtonRenderer {
    private params: any
    private eGui: any

    init (params: any): void {
      this.params = params

      const button = document.createElement('button')
      button.classList.add('button')
      button.classList.add('is-small')
      button.style.verticalAlign = 'baseline'
      button.type = 'button'

      if (params.value.style !== undefined) {
        button.classList.add(params.value.style)
      }

      this.eGui = button
      this.eGui.innerHTML = params.value.label

      this.eGui.addEventListener('click', this.params.value.onClick)
    }

    getGui (): any {
      return this.eGui
    }
}

export { ButtonRenderer }
