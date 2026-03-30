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

function envoyerMessage() {
    const messageInput = document.getElementById('message_input');
    const messageList = document.getElementById('message_list');
    const usernameSpan = document.getElementById('username');
    const username = usernameSpan.textContent.trim() || "Moi"; // Valeur par défaut si vide
    const text = messageInput.value.trim();
    if (text !== "") {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message sent';
        // Ajoute le username à côté du message
        msgDiv.innerHTML = `<span class="msg-username">${username} :</span> <span class="msg-text">${text}</span>`;
        messageList.appendChild(msgDiv);
        messageInput.value = "";
        messageList.parentElement.scrollTop = messageList.parentElement.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('send_button').addEventListener('click', envoyerMessage);
    document.getElementById('message_input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') envoyerMessage();
    });
});






