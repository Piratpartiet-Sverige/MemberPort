/*
 * Renders checkboxes in an ag-grid
 */

class CheckboxRenderer {
    private params: any
    private eGui: any

    init (params: any) {
        this.params = params;
    
        this.eGui = document.createElement('input');
        this.eGui.type = 'checkbox';
        this.eGui.checked = params.value.checked;
        this.eGui.disabled = typeof params.value.disabled !== 'undefined' ? params.value.disabled : false
    
        this.checkedHandler = this.checkedHandler.bind(this);
        this.eGui.addEventListener('click', this.checkedHandler);
    }

    getGui () {
        return this.eGui
    }

    checkedHandler (e: any) {
        let checked = e.target.checked;
        let colId = this.params.column.colId;
        this.params.node.setDataValue(colId, checked);
    }

    destroy () {
        this.eGui?.removeEventListener('click', this.checkedHandler);
    }
}
/*
function CheckboxRenderer() { }

CheckboxRenderer.prototype.init = function (params) {
    this.params = params;

    this.eGui = document.createElement('input');
    this.eGui.type = 'checkbox';
    this.eGui.checked = params.value.checked;
    this.eGui.disabled = typeof params.value.disabled !== 'undefined' ? params.value.disabled : false

    this.checkedHandler = this.checkedHandler.bind(this);
    this.eGui.addEventListener('click', this.checkedHandler);
}

CheckboxRenderer.prototype.checkedHandler = function (e) {
    let checked = e.target.checked;
    let colId = this.params.column.colId;
    this.params.node.setDataValue(colId, checked);
}

CheckboxRenderer.prototype.getGui = function (params) {
    return this.eGui;
}

CheckboxRenderer.prototype.destroy = function (params) {
    this.eGui.removeEventListener('click', this.checkedHandler);
}
*/
export { CheckboxRenderer }
