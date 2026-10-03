(() => {
    const picker = document.querySelector("[data-tech-stack-picker]");
    if (!picker) return;
    const groups = picker.querySelector("[data-radio-groups]");
    const addButton = picker.querySelector("[data-add-group]");
    const template = groups.firstElementChild.cloneNode(true);
    let nextIndex = groups.children.length;

    function update() {
        const selected = new Set(Array.from(groups.querySelectorAll("input:checked"), input => input.value));
        Array.from(groups.children).forEach((group, index) => {
            group.querySelector("[data-group-number]").textContent = index + 1;
            group.querySelector("[data-remove-group]").hidden = groups.children.length === 1;
            group.querySelectorAll("input").forEach(input => {
                input.disabled = selected.has(input.value) && !input.checked;
            });
        });
        addButton.disabled = groups.children.length >= template.querySelectorAll("input").length;
    }

    addButton.hidden = false;
    addButton.addEventListener("click", () => {
        const group = template.cloneNode(true);
        const index = nextIndex++;
        group.querySelectorAll("input").forEach((input, optionIndex) => {
            input.checked = false;
            input.name = `${picker.dataset.fieldName}_${index}`;
            input.id = `${picker.id}_${index}_${optionIndex}`;
            input.closest("label").htmlFor = input.id;
        });
        groups.appendChild(group);
        update();
        group.querySelector("input:not(:disabled)")?.focus();
    });
    groups.addEventListener("change", update);
    groups.addEventListener("click", event => {
        if (!event.target.matches("[data-remove-group]")) return;
        event.target.closest("[data-radio-group]").remove();
        update();
        addButton.focus();
    });
    update();
})();
