const modal = document.getElementById("task-modal");

document.getElementById("open-modal").onclick = function () {
    modal.style.display = "flex";
};

document.getElementById("close-modal").onclick = function () {
    modal.style.display = "none";
};

window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};

document.querySelectorAll(".edit-button").forEach(button => {
    button.onclick = function(){
        const id = this.dataset.taskId;
        document
        .getElementById(`edit-modal-${id}`)
        .style.display = "flex";

    };

});


document.querySelectorAll(".close-edit-modal").forEach(button => {
    button.onclick = function(){
        const id = this.dataset.taskId;
        document
        .getElementById(`edit-modal-${id}`)
        .style.display = "none";

    };

});

document.querySelectorAll("details[id]").forEach(details => {
    const storageKey = `details-open-${details.id}`;
    const storedState = localStorage.getItem(storageKey);

    if (storedState !== null) {
        details.open = storedState === "true";
    }

    details.addEventListener("toggle", () => {
        localStorage.setItem(storageKey, details.open);
    });
});
