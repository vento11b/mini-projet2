
function login(username, password) {
    fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password}),
    credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
    if (data.message) {
        alert(data.message);
        if (data.message.status == 1) {
            window.location.href = "/app";
        }
        else {
            alert("Error de login");
        }
    }
    });
}