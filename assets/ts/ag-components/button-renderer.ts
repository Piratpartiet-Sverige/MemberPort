import { Component } from '@ag-grid-community/all-modules'

/*
 * Renders buttons in an ag-grid
 */
class ButtonRenderer {
    private params: any
    private eGui: any

    init (params: any) {
        this.params = params

        this.eGui = document.createElement('button')
        // this.eGui.type = 'button'
        this.eGui.innerHTML = params.value.label

        this.eGui.addEventListener('click', this.params.value.onClick)
    }

    getGui () {
        return this.eGui
    }
    
    destroy () {
        // this.eGui.removeEventListener('click', this.clickHandler);
    }
}
/*
function ButtonRenderer() { }

ButtonRenderer.prototype.init = function (params) {
    this.params = params

    this.eGui = document.createElement('button')
    this.eGui.type = 'button'
    this.eGui.innerHTML = params.value.label

    this.eGui.addEventListener('click', this.params.value.onClick)
}

ButtonRenderer.prototype.getGui = function (params) {
    return this.eGui
}

ButtonRenderer.prototype.destroy = function (params) {
    this.eGui.removeEventListener('click', this.clickHandler);
}
*/
export { ButtonRenderer }
