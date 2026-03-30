
function deconnexion() {
    fetch('/app/deconnexion', {method: 'POST'}).then(resp => resp.json()).then(data =>{
        if (data.status) {
            window.location.href = "/connexion";
        }
    });
}

function add_friend(friend) {
    fetch("/app/ajouter/"+friend, {method: 'POST'}).then(resp => resp.json()).then(data =>{
        console.log(data);
    });

}


function add_friend(friend) {
    fetch('/app/ajouter/'+friend, {method: 'POST'}).then(resp => resp.json()).then(data =>{
        console.log(data);
    });
}

function add_contact(name, type) {
    let contacts = document.getElementById("contact_list");
    let contact = document.createElement("div")
    contact.className = "contact"
    contact.textContent = name
    contacts.appendChild(contact)
}