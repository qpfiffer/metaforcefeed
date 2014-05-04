function ping_object(e) {
    var dom_ele = e.target;
    var slug = dom_ele.getAttribute("data-slug");

    httpRequest = new XMLHttpRequest();
    httpRequest.open("POST", ping_url.replace("0", slug));
    httpRequest.setRequestHeader("Content-Type", "application/json");
    httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState == 4 && httpRequest.status == 200) {
            console.log("Response: ", httpRequest.responseText);
            var resp_json = JSON.parse(httpRequest.responseText);
            var error_ele = dom_ele.parentElement.getElementsByClassName("error")[0];
            if (resp_json.success) {
                var pings_ele = dom_ele.parentElement.getElementsByClassName("pings")[0];
                pings_ele.innerText = resp_json.ping_obj.pings;
                error_ele.innerText = "";
                dom_ele.onclick = function() { return true; };
            } else {
                error_ele.innerText = resp_json.error;
            }
        }
    }
    data = {"_csrf_token": csrf_token};
    httpRequest.send(JSON.stringify(data));

    return true;
}

function ping_init() {
    all_pingable = document.getElementsByClassName("arrow_up");
    for (var i = 0; i < all_pingable.length; i++) {
        all_pingable[i].onclick = ping_object;
    }
}
