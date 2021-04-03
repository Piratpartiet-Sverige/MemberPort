import { Component } from '@ag-grid-community/all-modules'

/*
 * Renders buttons in an ag-grid
 */
class ButtonRenderer {
    private params: any
    private eGui: any

    init (params: any): void {
      this.params = params

      this.eGui = document.createElement('button')
      // this.eGui.type = 'button'
      this.eGui.innerHTML = params.value.label

      this.eGui.addEventListener('click', this.params.value.onClick)
    }

    getGui (): any {
      return this.eGui
    }
}

export { ButtonRenderer }
