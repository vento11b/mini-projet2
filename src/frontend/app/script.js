let currentChat = null;
let currentType = null;



window.onload = () => {
    update();

    const input = document.getElementById("message_input");

    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();

            if (input.value.trim() !== "") {
                sendMessage();
            }
        }
    });

    const imageInput = document.getElementById("image_input");
    imageInput.addEventListener("change", function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById("preview_img").src = e.target.result;
                document.getElementById("image_preview").style.display = "block";
            };
            reader.readAsDataURL(file);
        }
    });
};


async function update() {
    const res = await fetch("/app/info", { method: "POST" });
    const data = await res.json();
    
    if (data.status !== 1) return;
    
    document.getElementById("username").innerText = data.info.username;
    
    renderContacts(
        data.info.amis,
        data.info.requetes_amis,
        data.info.salons
    );
    
    loadChatFromURL();
}

async function acceptFriend(username) {
    const res = await fetch(`/app/ajouter/${username}`, {
        method: "POST"
    });

    res.json();

    update();
}

let lastcontacts = []
function renderContacts(friends, requests, channels) {
    if (JSON.stringify([friends, requests, channels]) === JSON.stringify(lastcontacts)) return;
    
    lastcontacts = [friends, requests, channels]
    console.log("contacts")
    const list = document.getElementById("contact_list");
    list.innerHTML = "";

    friends.forEach(friend => {
        const div = document.createElement("div");
        div.classList.add("contact", "friend");

        div.innerHTML = `
            <span>${friend}</span>
        `;

        div.onclick = () => openFriendChat(friend);
        list.appendChild(div);
    });

    requests.forEach(req => {
        const div = document.createElement("div");
        div.classList.add("contact", "request");

        //✔
        div.innerHTML = `
            <span>${req}</span>
            <button class="accept-btn">+</button>
        `;

        div.querySelector(".accept-btn").onclick = (e) => {
            e.stopPropagation();
            acceptFriend(req);
        };

        list.appendChild(div);
    });

    
    channels.forEach(channel => {
        const div = document.createElement("div");
        div.classList.add("contact", "channel");

        div.innerHTML = `
            <span>${channel}</span>
        `;

        div.onclick = () => openChannelChat(channel);
        list.appendChild(div);
    });
}

function loadChatFromURL() {
    const params = new URLSearchParams(window.location.search);
    
    
    const type = params.get("type");
    const chat = params.get("chat");
    
    if (!type || !chat) return;
    
    if (type === "friend") {
        openFriendChat(chat);
    } else if (type === "channel") {
        openChannelChat(chat);
    }

}


function openFriendChat(friend) {
    currentChat = friend;
    currentType = "friend";

    const url = new URL(window.location);
    url.searchParams.set("type", "friend");
    url.searchParams.set("chat", friend);
    window.history.pushState({}, "", url);

    document.getElementById("chat-info").innerText = friend;

    loadMessages();
}

function openChannelChat(channel) {
    currentChat = channel;
    currentType = "channel";

    const url = new URL(window.location);
    url.searchParams.set("type", "channel");
    url.searchParams.set("chat", channel);
    window.history.pushState({}, "", url);

    document.getElementById("chat-info").innerText = "Salon " + channel;

    loadMessages();
}

let lastmessages = {}
async function loadMessages() {
    if (!currentChat) return;

    let url = "";

    if (currentType === "friend") {
        url = `/app/ami/messages/${currentChat}`;
    } else {
        url = `/app/salon/messages/${currentChat}`;
    }

    const res = await fetch(url, { method: "POST" });
    const data = await res.json();

    if (data.status !== 1) return;
    if (JSON.stringify(data.info) !== JSON.stringify(lastmessages)) {
        lastmessages = data.info;
        renderMessages(data.info);
    }
}

function renderMessages(messages) {
    const container = document.getElementById("message_list");
    const currentUser = document.getElementById("username").innerText.trim();

    container.innerHTML = "";
    
    const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 10;

    messages.forEach(msg => {
        const [id, sender, content, message_type, time] = msg;
        
        if (document.getElementById(`msg-${id}`)) return;

        const div = document.createElement("div");
        div.classList.add("message");
        div.id = `msg-${id}`;

        if (sender === currentUser) {
            div.classList.add("self");
        } else {
            div.classList.add("received");
        }

        let contentHtml;
        if (message_type === 'image') {
            contentHtml = `<img src="${content}" alt="Image" style="max-width: 200px; max-height: 200px;">`;
        } else {
            contentHtml = `<div class="msg-text" style="white-space: pre-wrap;">${content}</div>`;
        }

        div.innerHTML = `
            <div class="msg-header">
                <span class="msg-user">${sender}</span>
                <span class="msg-time">${time}</span>
            </div>
            ${contentHtml}
        `;

        container.appendChild(div);
    });

    if (isAtBottom) {
        container.scrollTop = container.scrollHeight;
    }
}


async function sendMessage() {
    if (!currentChat) return;
    const input = document.getElementById("message_input");
    const imageInput = document.getElementById("image_input");
    const text = input.value.trim();
    const file = imageInput.files[0];

    if (!text && !file) return;

    let url, body, headers;
    if (currentType === "friend") {
        url = `/app/ami/envoyer/${currentChat}`;
    } else {
        url = `/app/salon/envoyer/${currentChat}`;
    }

    if (file) {
        // Enviar como FormData para la imagen
        const formData = new FormData();
        formData.append('image', file);
        body = formData;
        headers = {};
    } else {
        // Enviar como JSON para texto
        body = JSON.stringify({ message: text });
        headers = { "Content-Type": "application/json" };
    }

    const res = await fetch(url, {
        method: "POST",
        headers: headers,
        body: body
    });

    const data = await res.json();
    if (data.status === 1) {
        input.value = "";
        imageInput.value = "";  // Limpiar el input de imagen
        removeImage();  // Ocultar preview
        loadMessages();
    } else {
        alert("Erreur lors de l'envoi: " + data.info);
    }
}


function removeImage() {
    document.getElementById("image_preview").style.display = "none";
    document.getElementById("preview_img").src = "";
    document.getElementById("image_input").value = "";
}

document.querySelector("#input button").onclick = sendMessage;


async function addFriend(name) {
    if (!name) return;

    const res = await fetch(`/app/ajouter/${name}`, { method: "POST" });
    const data = await res.json();

    //alert(data.info);

    update();
}

async function addChannel() {
    const input = document.getElementById("addchannel");
    const channelName = input.value.trim();
    if (!channelName) return;

    const res = await fetch(`/app/joindre/${channelName}`, { method: "POST" });
    const data = await res.json();

    if (data.status === 1) {
        input.value = "";
        update();
    }
}


async function deconnexion() {
    await fetch("/app/deconnexion", { method: "POST" });
    location.reload();
}


setInterval(() => {
    update();
}, 1000);