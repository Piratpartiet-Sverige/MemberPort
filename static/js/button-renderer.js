/*
 * Renders buttons in an ag-grid
 */
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