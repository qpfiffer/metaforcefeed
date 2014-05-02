function ping_object(e) {
    var dom_ele = e.target;
    var slug = dom_ele.getAttribute("data-slug");
    console.log(slug);
    return true;
}

function ping_init() {
    all_pingable = document.getElementsByClassName("arrow_up");
    for (var i = 0; i < all_pingable.length; i++) {
        var dom_ele = all_pingable[i];
        var slug = dom_ele.getAttribute("data-slug");
        dom_ele.onclick = ping_object;
    }
}
