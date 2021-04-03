/*
 * Renders checkboxes in an ag-grid
 */

class CheckboxRenderer {
    private params: any
    private eGui: any

    init (params: any): void {
      this.params = params

      this.eGui = document.createElement('input')
      this.eGui.type = 'checkbox'
      this.eGui.checked = params.value.checked
      this.eGui.disabled = typeof params.value.disabled !== 'undefined' ? params.value.disabled : false

      this.checkedHandler = this.checkedHandler.bind(this)
      this.eGui.addEventListener('click', this.checkedHandler)
    }

    getGui (): any {
      return this.eGui
    }

    checkedHandler (e: any): void {
      const checked = e.target.checked
      const colId = this.params.column.colId
      this.params.node.setDataValue(colId, checked)
    }

    destroy (): void {
      this.eGui?.removeEventListener('click', this.checkedHandler)
    }
}

export { CheckboxRenderer }
