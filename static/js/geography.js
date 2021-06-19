var geodata = {};
let listOfCommands = [];

function createEnum(values) {
    const enumObject = {};

    for (const val of values) {
        enumObject[val] = val;
    }

    return Object.freeze(enumObject);
}

const GEO_TYPES = createEnum(['COUNTRY', 'AREA', 'MUNICIPALITY']);
const GEO_ACTIONS = createEnum(['RENAME', 'MOVE', 'CREATE', 'DELETE']);

function saveGeography() {
    for (index in listOfCommands) {
        let command = listOfCommands[index];

        switch (command.action) {
            case GEO_ACTIONS.RENAME:
                if (command.type === GEO_TYPES.COUNTRY) {
                    renameCountry(command);
                } else if (command.type === GEO_TYPES.AREA) {
                    renameArea(command);
                } else if (command.type === GEO_TYPES.MUNICIPALITY) {
                    renameMunicipality(command);
                }

                break;
            case GEO_ACTIONS.MOVE:
                break;
            case GEO_ACTIONS.CREATE:
                break;
            case GEO_ACTIONS.DELETE:
                break;
        }
    }
}

function renameCountry(command) {
    sendUpdateCountryDataRequest(command.id, command.newName);
}

function renameArea(command) {
    console.log("STUB");
}

function renameMunicipality(command) {
    console.log("STUB");
}

function addArea(id, name, parent) {
    var parent = document.getElementById(parent);
    var area = createArea(id, name, true, "true", "fa-layer-group");

    parent.appendChild(area);
}

function addMunicipality(id, name, parent) {
    var parent = document.getElementById(parent);
    var area = createArea(id, name, false, "true", "fa-home");

    parent.appendChild(area);
}

function addCountry(id, name) {
    var tree = document.getElementById("tree");
    var country = createArea(id, name, true, "false", "fa-flag");

    tree.appendChild(country);
}

function createArea(id, name, hasDropzone, draggable, icon) {
    var area = document.createElement("div");
    area.setAttribute("id", id);
    area.setAttribute("draggable", draggable);

    if (draggable === "true") {
        area.setAttribute("ondragstart", "startDrag(event)");
        area.setAttribute("ondragend", "stopDrag(event)");
    }

    area.classList.add("node");

    var nameBox = createNameBox(id, name, icon);
    area.appendChild(nameBox);

    if (hasDropzone) {
        var dropzone = createDropZone();
        area.appendChild(dropzone);
    }

    return area;
}

function createNameBox(id, name, icon) {
    var nameBox = document.createElement("div");
    nameBox.classList.add("box");
    nameBox.innerHTML =
        "<article class='media'>" +
        "<div class='media-left'>" +
        "<span class='icon'><i class='fas " + icon + "'></i></span>" +
        "</div>" +
        "<div class='media-content'>" +
        "<div class='content'>" +
        name +
        "</div>" +
        "</div>" +
        "<div class='media-right'>" +
        "<a class='editPen' onclick='openEditModal(\"" + id + "\");'><span class='icon'><i class='fas fa-pen'></i></span></a>" +
        "<a onclick='shrinkList(\"" + id + "\");'><span class='icon'><i class='fas fa-angle-up'></i></span></a>" +
        "<span style='display: inline-block; width: 1rem;'></span>" +
        "<button onclick='openDeleteModal(\"" + id + "\");' class='delete'></button>" +
        "</div>" +
        "</article>";
    return nameBox;
}

function createDropZone() {
    var dropzone = document.createElement("div");
    dropzone.setAttribute("ondrop", "onDrop(event)");
    dropzone.setAttribute("ondragover", "allowDrop(event)");
    dropzone.classList.add("dropzone");
    dropzone.classList.add("is-hidden");
    dropzone.innerHTML = '<span class="icon is-large"><i class="fas fa-plus"></i></span>';

    return dropzone;
}

function allowDrop(ev) {
    ev.preventDefault();
}

function expandList(id) {
    var root = document.getElementById(id);
    var children = root.childNodes;

    for (var i = 0; i < children.length; i++) {
        if (children[i].classList !== undefined && children[i].classList.contains("node") === true) {
            children[i].style.display = "";
        }
    }
    var icon = root.getElementsByClassName("fa-angle-down")[0];

    if (icon !== undefined) {
        icon.classList.remove("fa-angle-down");
        icon.classList.add("fa-angle-up");
        var button = icon.parentElement.parentElement;
        button.setAttribute("onclick", "shrinkList('" + id + "');");
    }
}

function shrinkList(id) {
    var root = document.getElementById(id);
    var children = root.childNodes;

    for (var i = 0; i < children.length; i++) {
        if (children[i].classList !== undefined && children[i].classList.contains("node") === true) {
            children[i].style.display = "none";
        }
    }

    var icon = root.getElementsByClassName("fa-angle-up")[0];

    if (icon !== undefined) {
        icon.classList.remove("fa-angle-up");
        icon.classList.add("fa-angle-down");
        var button = icon.parentElement.parentElement;
        button.setAttribute("onclick", "expandList('" + id + "');");
    }
}


function startDrag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
    showDropZones(ev.target);
}

function showDropZones(draggedNode) {
    var dropzones = document.getElementsByClassName("dropzone");
    for (var i = 0; i < dropzones.length; i++) {
        dropzones[i].classList.remove("is-hidden");
    }

    var childDropzones = draggedNode.getElementsByClassName("dropzone");
    for (var i = 0; i < childDropzones.length; i++) {
        childDropzones[i].classList.add("is-hidden");
    }

    var parent = draggedNode.parentElement;
    var parentDropzone = parent.getElementsByClassName("dropzone")[0];
    parentDropzone.classList.add("is-hidden");
}

function hideDropZones() {
    var elements = document.getElementsByClassName("dropzone");
    for (var i = 0; i < elements.length; i++) {
        elements[i].classList.add("is-hidden");
    }
}

function stopDrag(ev) {
    hideDropZones();
}

function onDrop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");

    var node = ev.target;

    while (node.classList === undefined || node.classList.contains("dropzone") !== true) {
        node = ev.target.parentElement;
    }

    node.insertAdjacentElement("afterend", document.getElementById(data));
}

function findNearestNode(nodes) {
    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].classList !== undefined && nodes[i].classList.contains("node")) {
            return nodes[i];
        }
    }
}

function deleteNode(id) {
    var node = document.getElementById(id);
    node.remove();
}

function closeDeleteModal() {
    var deleteModal = document.getElementById("deleteModal");
    deleteModal.classList.remove("is-active");
}

function openDeleteModal(id) {
    var deleteModal = document.getElementById("deleteModal");
    deleteModal.classList.add("is-active");

    var deleteText = document.getElementById("deleteText");
    deleteText.innerText = "Är du säker på att du vill ta bort " + geodata[id].name + " och alla områden och kommuner som tillhör det?";

    var deleteNodeButton = document.getElementById("deleteNodeButton");
    deleteNodeButton.setAttribute("onclick", "deleteNode('" + id + "');closeDeleteModal();");
}

function closeEditModal() {
    var editModal = document.getElementById("editModal");
    editModal.classList.remove("is-active");
}

function openEditModal(id) {
    var editModal = document.getElementById("editModal");
    editModal.classList.add("is-active");

    var editNameButton = document.getElementById("editNameButton");
    editNameButton.setAttribute("onclick", "changeNodeName('" + geodata[id].id + "');closeEditModal();");

    var newNameInput = document.getElementById("newName");
    newNameInput.value = geodata[id].name;
}

function changeNodeName(id) {
    var node = document.getElementById(id);
    var newNameInput = document.getElementById("newName");
    var newName = newNameInput.value;

    var nameBox = node.getElementsByClassName("content")[0];
    nameBox.innerText = newName;
    geodata[id].name = newName;

    let command = {};
    command["id"] = id;
    command["type"] = getNodeType(id);
    command["action"] = GEO_ACTIONS.RENAME;
    command["newName"] = newName;

    var indexRemove = -1;

    for (var i = 0; i < listOfCommands.length; i++) {
        if (listOfCommands[i].id === command.id && listOfCommands[i].action === GEO_ACTIONS.RENAME) {
            indexRemove = i;
            break;
        }
    }

    if (indexRemove !== -1) {
        listOfCommands.splice(indexRemove, 1);
    }

    listOfCommands.push(command);
}

function getNodeType(id) {
    if (geodata[id]["path"] !== undefined) {
        return GEO_TYPES.AREA;
    } else if (geodata[id]["area"] !== undefined) {
        return GEO_TYPES.MUNICIPALITY;
    } else {
        return GEO_TYPES.COUNTRY;
    }
}

function getParentID(id, path, fallbackID) {
    var parentID = "";

    if (path === id) {
        parentID = fallbackID;
    } else {
        var count = (path.match(/./g) || []).length;
        if (count === 1) {
            parentID = path.substring(0, path.indexOf('.'));
        } else {
            parentID = path.substring(path.lastIndexOf(".", path.lastIndexOf(".") - 1), path.lastIndexOf("."));
        }
    }

    return parentID;
}

document.getElementById("newName").oninput = function(e) {
    if (/^[a-zA-ZåäöÅÄÖ]+$/.test(e.data) === false) {
        this.value = this.value.slice(0, -e.data.length);
    }
};