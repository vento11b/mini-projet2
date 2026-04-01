let currentChat = null;
let currentType = null;



window.onload = () => {
    init();

    const input = document.getElementById("message_input");

    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();

            if (input.value.trim() !== "") {
                sendMessage();
            }
        }
    });
};


async function init() {
    const res = await fetch("/app/info", { method: "POST" });
    const data = await res.json();
    
    if (data.status !== 1) return;
    
    document.getElementById("username").innerText = data.info.username;

    loadChatFromURL();
    
    renderContacts(
        data.info.amis,
        data.info.requetes_amis,
        data.info.salons
    );
    
}

async function acceptFriend(username) {
    const res = await fetch(`/app/ajouter/${username}`, {
        method: "POST"
    });

    res.json();

    init();
}


function renderContacts(friends, requests, channels) {
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

        div.innerHTML = `
            <span>${req}</span>
            <button class="accept-btn">✔</button>
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

    // 👇 actualizar URL
    const url = new URL(window.location);
    url.searchParams.set("type", "channel");
    url.searchParams.set("chat", channel);
    window.history.pushState({}, "", url);

    document.getElementById("chat-info").innerText = "Salon " + channel;
    loadMessages();
}


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
    const currentUser = document.getElementById("username").innerText.trim();

    
    const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 10;

    messages.forEach(msg => {
        const [sender, text, time] = msg;

        
        if (document.getElementById(`msg-${time}`)) return;

        const div = document.createElement("div");
        div.classList.add("message");
        div.id = `msg-${time}`;

        if (sender === currentUser) {
            div.classList.add("self");
        } else {
            div.classList.add("received");
        }

        div.innerHTML = `
            <div class="msg-header">
                <span class="msg-user">${sender}</span>
                <span class="msg-time">${time}</span>
            </div>
            <div class="msg-text" style="white-space: pre-wrap;">${text}</div>
        `;

        container.appendChild(div);
    });

    if (isAtBottom) {
        container.scrollTop = container.scrollHeight;
    }
}


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


document.querySelector("#input button").onclick = sendMessage;


async function add_friend(name) {
    if (!name) return;

    const res = await fetch(`/app/ajouter/${name}`, { method: "POST" });
    const data = await res.json();

    //alert(data.info);

    init();
}


async function deconnexion() {
    await fetch("/app/deconnexion", { method: "POST" });
    location.reload();
}


setInterval(() => {
    init();
    if (currentChat) {
        loadMessages();
    }
}, 3000);