const handler = _ => {
    // First remove the last element of the filter select
    const classSelector = document.getElementById("from-class_select");
    const toRemove = document.querySelector("#from-class_select > option:nth-child(25)");
    classSelector?.removeChild(toRemove);

    // Then add text that helps teachers to know how to select multiple things
    const addText = document.querySelector("#changelist-filter > ul > li.selected");
    let p = document.createElement("p");
    p.innerHTML = "Drž CTRL pre označenie viacerých";
    p.style.padding = "0";
    p.style.color = "#c1beba70";
    p.style.textDecoration = "underline";
    addText?.append(p);

    // Lastly translate the page into slovak
    let selectText = document.querySelector("div#content > h1").innerHTML.split(" ");
    selectText[0] = selectText[0].replace("Select", "Označ");
    switch (selectText[1]) {
        case "Užívateľ":
            selectText[1] = selectText[1] + "ov";
            break;
        case "Správa":
        case "Téma":
            selectText[1] = selectText[1].replace("a", "y") + " " + selectText[2].slice(0, selectText[2].length - 1) + "í";
            selectText.splice(2, 1);
            break;
        case "Trieda":
            selectText[1] = selectText[1].replace("a", "y");
            break;
        case "Diskusia":
            selectText[1] = selectText[1].replace("a", "e");
            break;

        default:
            break;
    }
    if (selectText[2] != null) {
        selectText[2] = selectText[2].replace("to", "pre");
    }
    if (selectText[3] != null) {
        selectText[3] = selectText[3].replace("change", "zmenu");
    }
    document.querySelector("div#content > h1").innerHTML = document.querySelector("div#content > h1").innerHTML.replace(document.querySelector("div#content > h1").innerHTML, selectText.join(" "));

    let addButton = document.querySelector("#content-main > ul > li > a").innerHTML.trim();
    let addButtonArr = addButton.split(" ");
    addButtonArr[0] = "Pridať";
    addButtonArr[1] = selectText[1];
    addButton = addButtonArr.splice(0, 2).join(" ");
    document.querySelector("#content-main > ul > li > a").innerHTML = addButton;

    // Sidebar translation
    let authText = document.querySelector("#nav-sidebar > div.app-auth.module > table > caption > a");
    if (authText != null) {
        authText.innerHTML = "Autentifikácia a Autorizácia";
        document.querySelector("#nav-sidebar > div.app-auth.module > table > caption > a").innerHTML = authText.innerHTML;
    }

    let appText = document.querySelector("#nav-sidebar > div.app-base > table > caption > a");
    if (appText != null) {
        appText.innerHTML = "SPŠE Administrácia";
        document.querySelector("#nav-sidebar > div.app-base > table > caption > a").innerHTML = appText.innerHTML;
    }

    let onlineUsers = document.querySelector("#nav-sidebar > div.app-online_users.module > table > caption > a");
    if (onlineUsers != null) {
        onlineUsers.innerHTML = "Online užívatelia";
        document.querySelector("#nav-sidebar > div.app-online_users.module > table > caption > a").innerHTML = onlineUsers.innerHTML;
    }
    
    // Main content sidebar translation
    authText = document.querySelector("#content-main > div.app-auth.module > table > caption > a");
    if (authText != null) {
        authText.innerHTML = "Autentifikácia a Autorizácia";
        document.querySelector("#content-main > div.app-auth.module > table > caption > a").innerHTML = authText.innerHTML;
    }

    appText = document.querySelector("#content-main > div.app-base > table > caption > a");
    if (appText != null) {
        appText.innerHTML = "SPŠE Administrácia";
        document.querySelector("#content-main > div.app-base > table > caption > a").innerHTML = appText.innerHTML;
    }

    onlineUsers = document.querySelector("#content-main > div.app-online_users.module > table > caption > a");
    if (onlineUsers != null) {
        onlineUsers.innerHTML = "Online užívatelia";
        document.querySelector("#content-main > div.app-online_users.module > table > caption > a").innerHTML = onlineUsers.innerHTML;
    }
    const change = document.querySelector("#content > h1");
    if (change != null) {
        change.innerHTML = change.innerHTML.replace("Change", "Zmeniť");
    }
}
document.addEventListener('DOMContentLoaded', handler)