import { sendUpdateCountryDataRequest, sendUpdateAreaDataRequest, sendUpdateMunicipalityDataRequest } from './api.ts'
import { afterPageLoad } from '../utils/after-page-load'

class GeoData {
    id: string
    name: string
    path: string|undefined
    area: string|undefined

    constructor(id: string, name: string, path: string|undefined, area: string|undefined) {
        this.id = id;
        this.name = name;
        this.path = path;
        this.area = area;
    }
}

declare let geodata: { [id: string]: GeoData };
declare let selectedCountryID: string;
let listOfCommands: GeoCommand[] = [];

enum GEO_TYPES {
    COUNTRY,
    AREA,
    MUNICIPALITY,
}

enum GEO_ACTIONS {
    RENAME,
    MOVE,
    CREATE,
    DELETE,
}

class GeoCommand {
    constructor(id: string, newName: string, action: GEO_ACTIONS, type: GEO_TYPES) {
        this.id = id;
        this.newName = newName;
        this.action = action;
        this.type = type;
    }

    action: GEO_ACTIONS;
    type: GEO_TYPES;
    id: string = "";
    newName: string = "";
}

function saveGeography() {
    if (listOfCommands.length === 0) {
        console.log("No changes detected");
        createMessage("Inga ändringar upptäcktes", "is-info")
        return;
    }

    for (let index = 0; index < listOfCommands.length; index++) {
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

    listOfCommands = [];
}

function renameCountry(command: GeoCommand) {
    sendUpdateCountryDataRequest(command.id, command.newName)
        .then(function(response: Response) {
            return response.json();
        })
        .then(function(data: { [name: string]: any }) {
            if (data["success"] === false) {
                throw new Error(data["reason"]);
            }

            createMessage("Ändrat namn på landet till: " + command.newName, "is-success");
        }).catch((error: string) => {
            console.error('Error:', error);
            createMessage("Någonting gick fel när namnet på landet skulle uppdateras", "is-danger");
        });
}

function renameArea(command: GeoCommand) {
    sendUpdateAreaDataRequest(command.id, command.newName, null, null)
        .then(function(response: Response) {
            return response.json();
        })
        .then(function(data: { [name: string]: any }) {
            if (data["success"] === false) {
                throw new Error(data["reason"]);
            }

            createMessage("Ändrat namn på området till: " + command.newName, "is-success");
        }).catch((error: string) => {
            console.error('Error:', error);
            createMessage("Någonting gick fel när namnet på området skulle uppdateras", "is-danger");
        });
}

function renameMunicipality(command: GeoCommand) {
    sendUpdateMunicipalityDataRequest(command.id, command.newName, null, null)
        .then(function(response: Response) {
            return response.json();
        })
        .then(function(data: { [name: string]: any }) {
            if (data["success"] === false) {
                throw new Error(data["reason"]);
            }

            createMessage("Ändrat namn på kommunen till: " + command.newName, "is-success");
        }).catch((error: string) => {
            console.error('Error:', error);
            createMessage("Någonting gick fel när namnet på kommunen skulle uppdateras", "is-danger");
        });
}

function createMessage(message: string, type: string) {
    let tree = document.getElementById("tree");
    let messageDiv = document.createElement("div");
    messageDiv.classList.add("notification");
    messageDiv.classList.add(type);

    let button = document.createElement("button");
    button.type = "button";
    button.classList.add("delete");
    button.onclick = () => { messageDiv.remove() };

    let text = document.createElement("p");
    text.textContent = message;

    messageDiv.appendChild(button);
    messageDiv.appendChild(text);

    if (tree !== null) {
        tree.insertAdjacentElement('beforebegin', messageDiv);
    }
}

function addArea(id: string, name: string, parent: string) {
    let parentElement = document.getElementById(parent);
    let area = createArea(id, name, true, true, "fa-layer-group");

    if (parentElement != null) {
        parentElement.appendChild(area);
    }
}

function addMunicipality(id: string, name: string, parent: string) {
    let parentElement = document.getElementById(parent);
    let area = createArea(id, name, false, true, "fa-home");

    if (parentElement != null) {
        parentElement.appendChild(area);
    }
}

function addCountry(id: string, name: string) {
    let tree = document.getElementById("tree");
    let country = createArea(id, name, true, false, "fa-flag");

    if (tree != null) {
        tree.appendChild(country);
    }
}

function createArea(id: string, name: string, hasDropzone: boolean, draggable: boolean, icon: string) {
    let area = document.createElement("div");
    area.id = id;
    area.draggable = draggable;

    if (draggable) {
        area.ondragstart = (event) => { startDrag(event) };
        area.ondragend = (event) => { stopDrag(event) };
    }

    area.classList.add("node");

    let nameBox = createNameBox(id, name, icon);
    area.appendChild(nameBox);

    if (hasDropzone) {
        let dropzone = createDropZone();
        area.appendChild(dropzone);
    }

    return area;
}

function createNameBox(id: string, name: string, icon: string) {
    let nameBox = document.createElement("div");
    nameBox.classList.add("box");
    
    let article = document.createElement("article");
    article.classList.add("media");

    let divLeft = document.createElement("div");
    divLeft.classList.add("media-left");

    let areaIconContainer = document.createElement("span");
    areaIconContainer.classList.add("icon");

    let areaIcon = document.createElement("i");
    areaIcon.classList.add("fas");
    areaIcon.classList.add(icon);

    let divMediaContent = document.createElement("div");
    divMediaContent.classList.add("media-content");

    let divContent = document.createElement("div");
    divContent.classList.add("content");
    divContent.textContent = name;

    let divRight = document.createElement("div");
    divLeft.classList.add("media-right");

    let editPen = document.createElement("a");
    editPen.classList.add("editPen");
    editPen.onclick = () => { openEditModal(id) };

    let editPenIconContainer = document.createElement("span");
    editPenIconContainer.classList.add("icon");

    let editPenIcon = document.createElement("i");
    editPenIcon.classList.add("fas");
    editPenIcon.classList.add("fa-pen");

    let minimizeExpand = document.createElement("a");
    minimizeExpand.onclick = () => { shrinkList(id) };

    let arrowIconContainer = document.createElement("span");
    arrowIconContainer.classList.add("icon");

    let arrowIcon = document.createElement("i");
    arrowIcon.classList.add("fas");
    arrowIcon.classList.add("fa-angle-up");

    let filler = document.createElement("span");
    filler.style.display = "inline-block";
    filler.style.width = "1rem";

    let deleteButton = document.createElement("button");
    deleteButton.classList.add("delete");
    deleteButton.onclick = () => { openDeleteModal(id) };

    areaIconContainer.appendChild(areaIcon);
    divLeft.appendChild(areaIcon);

    divMediaContent.appendChild(divContent);

    editPenIconContainer.appendChild(editPenIcon);
    editPen.appendChild(editPenIconContainer);

    arrowIconContainer.appendChild(arrowIcon);
    minimizeExpand.appendChild(arrowIconContainer);

    divRight.appendChild(editPen);
    divRight.appendChild(minimizeExpand);
    divRight.appendChild(filler);
    divRight.appendChild(deleteButton);

    article.appendChild(divLeft);
    article.appendChild(divMediaContent);
    article.appendChild(divRight);

    nameBox.appendChild(article);
    return nameBox;
}

function createDropZone() {
    let dropzone = document.createElement("div");
    dropzone.ondrop = (event) => { onDrop(event) };
    dropzone.ondragover = (event) => { allowDrop(event) };
    dropzone.classList.add("dropzone");
    dropzone.classList.add("is-hidden");
    dropzone.innerHTML = '<span class="icon is-large"><i class="fas fa-plus"></i></span>';

    return dropzone;
}

function allowDrop(ev: Event) {
    ev.preventDefault();
}

function expandList(id: string) {
    let root = document.getElementById(id);

    if (root === null) {
        return;
    }

    let children = root.childNodes;

    for (let i = 0; i < children.length; i++) {
        let node = children[i] as HTMLElement;
        if (node.classList.contains("node") === true) {
            node.style.display = "";
        }
    }

    let icon = root.getElementsByClassName("fa-angle-down")[0];

    if (icon !== undefined) {
        icon.classList.remove("fa-angle-down");
        icon.classList.add("fa-angle-up");

        if (icon.parentElement !== null) {
            let button = icon.parentElement.parentElement;

            if (button !== null) {
                button.onclick = () => { shrinkList(id) };
            }
        }
    }
}

function shrinkList(id: string) {
    let root = document.getElementById(id);

    if (root === null) {
        return;
    }

    let children = root.childNodes;

    for (let i = 0; i < children.length; i++) {
        let node = children[i] as HTMLElement;
        if (node.classList.contains("node") === true) {
            node.style.display = "none";
        }
    }

    let icon = root.getElementsByClassName("fa-angle-up")[0];

    if (icon !== undefined) {
        icon.classList.remove("fa-angle-up");
        icon.classList.add("fa-angle-down");

        if (icon.parentElement !== null) {
            let button = icon.parentElement.parentElement;

            if (button !== null) {
                button.onclick = () => { expandList(id) };
            }
        }
    }
}


function startDrag(ev: DragEvent) {
    if (ev.dataTransfer !== null && ev.target !== null) {
        let targetElement = ev.target as Element;
        ev.dataTransfer.setData("text", targetElement.id);
        showDropZones(targetElement);
    }
}

function showDropZones(draggedNode: Element) {
    let dropzones = document.getElementsByClassName("dropzone");
    for (let i = 0; i < dropzones.length; i++) {
        dropzones[i].classList.remove("is-hidden");
    }

    let childDropzones = draggedNode.getElementsByClassName("dropzone");
    for (let i = 0; i < childDropzones.length; i++) {
        childDropzones[i].classList.add("is-hidden");
    }

    let parent = draggedNode.parentElement;

    if (parent !== null) { 
        let parentDropzone = parent.getElementsByClassName("dropzone")[0];
        parentDropzone.classList.add("is-hidden");
    }
}

function hideDropZones() {
    let elements = document.getElementsByClassName("dropzone");
    for (let i = 0; i < elements.length; i++) {
        elements[i].classList.add("is-hidden");
    }
}

function stopDrag(ev: Event) {
    hideDropZones();
}

function onDrop(ev: DragEvent) {
    ev.preventDefault();

    let data = "";

    if (ev.dataTransfer !== null) {
        data = ev.dataTransfer.getData("text");
    }

    let target = ev.target;

    if (target !== null) {
        let node = target as HTMLElement;
        let parent;

        while (node.classList.contains("dropzone") !== true && node.parentElement !== null) {
            node = node.parentElement;
        }

        let movedNode = document.getElementById(data);

        if (movedNode !== null) {
            node.insertAdjacentElement("afterend", movedNode);
        }
    }
}

function findNearestNode(nodes: HTMLElement[]) {
    for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].classList !== undefined && nodes[i].classList.contains("node")) {
            return nodes[i];
        }
    }
}

function deleteNode(id: string) {
    let node = document.getElementById(id);

    if (node !== null) {
        node.remove();
    }
}

function closeDeleteModal() {
    let deleteModal = document.getElementById("deleteModal");

    if (deleteModal !== null) {
        deleteModal.classList.remove("is-active");
    }
}

function openDeleteModal(id: string) {
    let deleteModal = document.getElementById("deleteModal");
    if (deleteModal !== null) {
        deleteModal.classList.add("is-active");
    }

    let deleteText = document.getElementById("deleteText");
    if (deleteText !== null) {
        deleteText.innerText = "Är du säker på att du vill ta bort " + geodata[id].name + " och alla områden och kommuner som tillhör det?";
    }

    let deleteNodeButton = document.getElementById("deleteNodeButton");
    if (deleteNodeButton !== null) {
        deleteNodeButton.onclick = () => { deleteNode(id); closeDeleteModal(); };
    }
}

function closeEditModal() {
    let editModal = document.getElementById("editModal");

    if (editModal !== null) {
        editModal.classList.remove("is-active");
    }
}

function openEditModal(id: string) {
    let editModal = document.getElementById("editModal");
    if (editModal !== null) {
        editModal.classList.add("is-active");
    }

    let editNameButton = document.getElementById("editNameButton");
    if (editNameButton !== null) {
        editNameButton.onclick = () => { changeNodeName(geodata[id].id); closeEditModal(); };
    }

    let newNameInput = document.getElementById("newName") as HTMLInputElement;
    if (newNameInput !== null) {
        newNameInput.value = geodata[id].name;
    }
}

function changeNodeName(id: string) {
    let node = document.getElementById(id);
    let newNameInput = document.getElementById("newName") as HTMLInputElement;

    if (node === null || newNameInput === null) {
        return;
    }

    let newName = newNameInput.value;

    let nameBox = node.getElementsByClassName("content")[0] as HTMLElement;
    nameBox.innerText = newName;
    geodata[id].name = newName;

    let command = new GeoCommand(id, newName, GEO_ACTIONS.RENAME, getNodeType(id));
    let indexRemove = -1;

    for (let i = 0; i < listOfCommands.length; i++) {
        if (listOfCommands[i].id === command.id && listOfCommands[i].action === GEO_ACTIONS.RENAME) {
            indexRemove = i;
            break;
        }
    }

    if (indexRemove !== -1) {
        listOfCommands.splice(indexRemove, 1);
    }

    console.log(command.newName);
    listOfCommands.push(command);
}

function getNodeType(id: string) {
    if (geodata[id].path !== undefined) {
        return GEO_TYPES.AREA;
    } else if (geodata[id].area !== undefined) {
        return GEO_TYPES.MUNICIPALITY;
    } else {
        return GEO_TYPES.COUNTRY;
    }
}

function getParentID(id: string, path: string, fallbackID: string) {
    let parentID = "";

    if (path === id) {
        parentID = fallbackID;
    } else {
        let count = (path.match(/./g) || []).length;
        if (count === 1) {
            parentID = path.substring(0, path.indexOf('.'));
        } else {
            parentID = path.substring(path.lastIndexOf(".", path.lastIndexOf(".") - 1), path.lastIndexOf("."));
        }
    }

    return parentID;
}

let newName = document.getElementById("newName") as HTMLInputElement;

if (newName !== null) {
    newName.oninput = function(event: Event) {
        let e = event as InputEvent;

        if (e.data !== null && /^[a-zA-ZåäöÅÄÖ]+$/.test(e.data) === false) {
            newName.value = newName.value.slice(0, -e.data.length);
        }
    };
}

afterPageLoad().then(() => {
    addCountry(selectedCountryID, geodata[selectedCountryID].name);
    let parentID = "";

    for (let id in geodata) {
        let data = geodata[id];

        // Check if this is an area
        if (data.path !== undefined) {
            parentID = getParentID(data.id, data.path, selectedCountryID);
            addArea(data.id, data.name, parentID);
        }
        // Check if this is a municipality
        else if (data.area !== undefined) {
            parentID = data.area;

            if (parentID === "") {
                parentID = selectedCountryID;
            }

            addMunicipality(data.id, data.name, parentID);
        }
    }

    let saveButton = document.getElementById("saveButton");
    if (saveButton !== null) {
        saveButton.onclick = () => { saveGeography() };
    }

    let cancelDeleteSmall = document.getElementById("cancelDeleteSmall");
    if (cancelDeleteSmall !== null) {
        cancelDeleteSmall.onclick = () => { closeDeleteModal() };
    }

    let cancelDelete = document.getElementById("cancelDelete");
    if (cancelDelete !== null) {
        cancelDelete.onclick = () => { closeDeleteModal() };
    }

    let cancelEditSmall = document.getElementById("cancelEditSmall");
    if (cancelEditSmall !== null) {
        cancelEditSmall.onclick = () => { closeEditModal() };
    }

    let cancelEdit = document.getElementById("cancelEdit");
    if (cancelEdit !== null) {
        cancelEdit.onclick = () => { closeEditModal() };
    }
}).catch(console.error)
  