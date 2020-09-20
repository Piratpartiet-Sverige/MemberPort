document.getElementById("newName").oninput = function(e) {
    if (/^[a-zA-ZåäöÅÄÖ]+$/.test(e.data) === false) {
        this.value = this.value.slice(0, -e.data.length);
    }
};

addCountry("Sverige");
addArea("Norrland", "Sverige");
addMunicipality("Luleå", "Norrland");
addMunicipality("Piteå", "Norrland");

function addArea(name, parent) {
    var parent = document.getElementById(parent);
    var area = createArea(name, true, "true", "fa-layer-group");

    parent.appendChild(area);
}

function addMunicipality(name, parent) {
    var parent = document.getElementById(parent);
    var area = createArea(name, false, "true", "fa-home");

    parent.appendChild(area);
}

function addCountry(name) {
    var tree = document.getElementById("tree");
    var country = createArea(name, true, "false", "fa-flag");

    tree.appendChild(country);
}

function createArea(name, hasDropzone, draggable, icon) {
    var area = document.createElement("div");
    area.setAttribute("id", name);
    area.setAttribute("draggable", draggable);

    if (draggable === "true") {
        area.setAttribute("ondragstart", "startDrag(event)");
        area.setAttribute("ondragend", "stopDrag(event)");
    }

    area.classList.add("node");

    var nameBox = createNameBox(name, icon);
    area.appendChild(nameBox);

    if (hasDropzone) {
        var dropzone = createDropZone();
        area.appendChild(dropzone);
    }

    return area;
}

function createNameBox(name, icon) {
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
        "<a class='editPen' onclick='openEditModal(\"" + name + "\");'><span class='icon'><i class='fas fa-pen'></i></span></a>" +
        "<a onclick='shrinkList(\"" + name + "\");'><span class='icon'><i class='fas fa-angle-up'></i></span></a>" +
        "<span style='display: inline-block; width: 1rem;'></span>" +
        "<button onclick='openDeleteModal(\"" + name + "\");' class='delete'></button>" +
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

    node.parentElement.appendChild(document.getElementById(data));
}

function findNearestNode(nodes) {
    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].classList !== undefined && nodes[i].classList.contains("node")) {
            return nodes[i];
        }
    }
}

function deleteNode(name) {
    var node = document.getElementById(name);
    node.remove();
}

function closeDeleteModal() {
    var deleteModal = document.getElementById("deleteModal");
    deleteModal.classList.remove("is-active");
}

function openDeleteModal(name) {
    var deleteModal = document.getElementById("deleteModal");
    deleteModal.classList.add("is-active");

    var deleteText = document.getElementById("deleteText");
    deleteText.innerText = "Är du säker på att du vill ta bort " + name + " och alla områden och kommuner som tillhör det?";

    var deleteNodeButton = document.getElementById("deleteNodeButton");
    deleteNodeButton.setAttribute("onclick", "deleteNode('" + name + "');closeDeleteModal();");
}

function closeEditModal() {
    var editModal = document.getElementById("editModal");
    editModal.classList.remove("is-active");
}

function openEditModal(name) {
    var editModal = document.getElementById("editModal");
    editModal.classList.add("is-active");

    var editNameButton = document.getElementById("editNameButton");
    editNameButton.setAttribute("onclick", "changeNodeName('" + name + "');closeEditModal();");

    var newNameInput = document.getElementById("newName");
    newNameInput.value = name;
}

function changeNodeName(name) {
    var node = document.getElementById(name);
    var newNameInput = document.getElementById("newName");
    var newName = newNameInput.value;

    node.id = newName;
    var nameBox = node.getElementsByClassName("content")[0];
    nameBox.innerText = newName;

    var editPen = node.getElementsByClassName("editPen")[0];
    editPen.setAttribute("onclick", "openEditModal(\"" + newName + "\");")
}

function getSiblings(node) {
    let siblings = [];

    if (!node.parentNode) {
        return siblings;
    }

    let sibling = node.parentNode.firstChild;

    while (sibling) {
        if (sibling.nodeType === 1 && sibling !== node) {
            siblings.push(sibling);
        }
        sibling = sibling.nextSibling;
    }
    return siblings;
};