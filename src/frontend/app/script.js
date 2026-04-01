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
        if (data.status) {
            add_contact(friend, "ami");    
        }
    });
    
}

function add_channel(channel) {
    fetch("/app/joindre/"+channel, {method: 'POST'}).then(resp => resp.json()).then(data =>{
        console.log(data);
        if (data.status) {
            add_contact(channel, "salon");
        }
    });
    
}



let contactlist = []
function add_contact(name, type) {
    
        let contacts = document.getElementById("contact_list");
        let contact = document.createElement("div")
        contact.classList = ["contact contact-"+type]
        contact.id = name
        contact.textContent = type+": "+name
        contacts.appendChild(contact)
    
}






function reloadInfo() {
    fetch('/app/info', {method: 'POST'}).then(resp => resp.json()).then(data =>{        
        document.getElementById("username").innerText = data.info.username

        if (data.info.amis.length>0) {
            add_contact(data.info.amis, "ami")
        }
        if (data.info.requetes_amis.length>0) {
            add_contact(data.info.requetes_amis, "requete");
        }
        if (data.info.salons.length>0) {
            add_contact(data.info.salons, "salon");
        }
    });
}


