function show_delete(e) {
    var delete_btn = document.getElementById("delete_btn");
    var delete_form = document.getElementById("delete_form");

    var reg = new RegExp('(\\s|^)hidden(\\s|$)');
    delete_form.className = delete_form.className.replace(reg,' ');
    delete_btn.className += 'hidden';
    return false;
}

function hide_delete(e) {
    var delete_btn = document.getElementById("delete_btn");
    var delete_form = document.getElementById("delete_form");

    var reg = new RegExp('(\\s|^)hidden(\\s|$)');
    delete_btn.className = delete_btn.className.replace(reg,' ');
    delete_form.className += 'hidden';
    return false;
}

function item_init() {
    delete_btn = document.getElementById("delete_btn");
    delete_btn.onclick = show_delete;

    nevermind = document.getElementById("nevermind");
    nevermind.onclick = hide_delete;
}
