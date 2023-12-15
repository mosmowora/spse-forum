const handler = e => {
    // First remove the last element of the filter select
    const classSelector = document.getElementById("from-class_select");
    const toRemove = document.querySelector("#from-class_select > option:nth-child(25)");
    classSelector.removeChild(toRemove);

    // Then add text that helps teachers to know how to select multiple things
    const addText = document.querySelector("#changelist-filter > ul > li.selected");
    let p = document.createElement("p");
    p.innerHTML = "Drž CTRL pre označenie viacerých";
    p.style.padding = "0";
    p.style.color = "#c1beba70";
    p.style.textDecoration = "underline";
    addText.append(p);
}
document.addEventListener('DOMContentLoaded', handler)