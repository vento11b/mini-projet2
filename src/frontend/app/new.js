let currentChat = null;
let currentType = null; // "friend" o "channel"

// ==========================
// INIT
// ==========================
async function init() {
    const res = await fetch("/app/info", { method: "POST" });
    const data = await res.json();

    if (data.status !== 1) return;

    document.getElementById("username").innerText = data.info.username;

    renderContacts(data.info.amis, data.info.salons);

    const input = document.getElementById("message_input");

    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();

            if (input.value.trim() !== "") {
                sendMessage();
            }
        }
    });
}

window.onload = init;

async function acceptFriend(username) {
    const res = await fetch(`/app/ajouter/${username}`, {
        method: "POST"
    });

    const data = await res.json();

    alert(data.info);

    init(); // refrescar lista
}

// ==========================
// RENDER CONTACTOS
// ==========================
function renderContacts(friends, requests, channels) {
    const list = document.getElementById("contact_list");
    list.innerHTML = "";

    // =====================
    // AMIGOS
    // =====================
    friends.forEach(friend => {
        const div = document.createElement("div");
        div.classList.add("contact", "friend");

        div.innerHTML = `
            <span>👤 ${friend}</span>
        `;

        div.onclick = () => openFriendChat(friend);
        list.appendChild(div);
    });

    // =====================
    // SOLICITUDES
    // =====================
    requests.forEach(req => {
        const div = document.createElement("div");
        div.classList.add("contact", "request");

        div.innerHTML = `
            <span>📩 ${req}</span>
            <button class="accept-btn">✔</button>
        `;

        // aceptar solicitud
        div.querySelector(".accept-btn").onclick = (e) => {
            e.stopPropagation();
            acceptFriend(req);
        };

        list.appendChild(div);
    });

    // =====================
    // CANALES
    // =====================
    channels.forEach(channel => {
        const div = document.createElement("div");
        div.classList.add("contact", "channel");

        div.innerHTML = `
            <span>📢 ${channel}</span>
        `;

        div.onclick = () => openChannelChat(channel);
        list.appendChild(div);
    });
}


// ==========================
// ABRIR CHAT
// ==========================
async function openFriendChat(friend) {
    currentChat = friend;
    currentType = "friend";
    document.getElementById("chat-info").innerText = friend;
    await loadMessages();
}

async function openChannelChat(channel) {
    currentChat = channel;
    currentType = "channel";
    document.getElementById("chat-info").innerText = "Salon " + channel;
    await loadMessages();
}


// ==========================
// CARGAR MENSAJES
// ==========================
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

    renderMessages(data.info);
}

function renderMessages(messages) {
    const container = document.getElementById("message_list");
    container.innerHTML = "";

    const currentUser = document.getElementById("username").innerText;

    messages.forEach(msg => {
        const sender = msg[0];
        const text = msg[1];
        const time = msg[2];

        const div = document.createElement("div");
        div.classList.add("message");

        if (sender === currentUser) {
            div.classList.add("self");
        }

        div.innerHTML = `
            <div class="msg-header">
                <span class="msg-user">${sender}</span>
                <span class="msg-time">${time}</span>
            </div>
            <div class="msg-text">${text}</div>
        `;

        container.appendChild(div);
    });

    container.scrollTop = container.scrollHeight;
}


// ==========================
// ENVIAR MENSAJE
// ==========================
async function sendMessage() {
    const input = document.querySelector("#input input");
    const message = input.value;

    if (!message || !currentChat) return;

    let url = "";

    if (currentType === "friend") {
        url = `/app/ami/envoyer/${currentChat}/${encodeURIComponent(message)}`;
    } else {
        url = `/app/salon/envoyer/${currentChat}/${encodeURIComponent(message)}`;
    }

    await fetch(url, { method: "POST" });

    input.value = "";
    await loadMessages();
}

// botón enviar
document.querySelector("#input button").onclick = sendMessage;


// ==========================
// AÑADIR AMIGO
// ==========================
async function add_friend(name) {
    if (!name) return;

    const res = await fetch(`/app/ajouter/${name}`, { method: "POST" });
    const data = await res.json();

    alert(data.info);

    init(); // recargar lista
}


// ==========================
// DESCONEXIÓN
// ==========================
async function deconnexion() {
    await fetch("/app/deconnexion", { method: "POST" });
    location.reload();
}


// ==========================
// AUTO REFRESH MENSAJES
// ==========================
setInterval(() => {
    if (currentChat) {
        loadMessages();
    }
}, 3000);