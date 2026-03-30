fetch("/app/info", {method: "POST"}).then(resp => resp.json()).then(data =>{
    document.getElementById("username").innerText = data.info.username
});

fetch("/app/amis", {method: "POST"}).then(resp => resp.json()).then(data =>{
    for (let i=0; i<data.info.length; i++) {
        add_contact(data.info[i])
    }
});

