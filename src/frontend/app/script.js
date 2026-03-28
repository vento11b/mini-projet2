function fetchjson(url) {
    fetch(url, {method: 'POST'}).then(resp => resp.json()).then(data =>{
        return data;
    });
}


function deconnexion() {
    fetch('/app/deconnexion').then(data => {
        console.log(data);
    });
    
}

function get_compte() {
    fetch('/app/compte', {method: 'POST'}).then(resp => resp.json()).then(data =>{
        console.log(data);
    });
}


function get_friends() {
    fetch('/app/amis', {method: 'POST'}).then(resp => resp.json()).then(data =>{
        console.log(data);
    });
}

function add_friend(friend) {
    fetch('/app/ajouter/'+friend, {method: 'POST'}).then(resp => resp.json()).then(data =>{
        console.log(data);
    });
}



