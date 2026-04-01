
fetch('/app/info', {method: 'POST'}).then(resp => resp.json()).then(data =>{
    console.log(document.getElementById("username"))
    console.log(data.info.username)
    //console.log(data);
    document.getElementById("username").innerText = data.info.username
});