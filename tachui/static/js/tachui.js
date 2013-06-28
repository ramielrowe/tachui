var csrftoken = $.cookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function clear_session(do_refresh){
    $.ajax({
        type: "DELETE",
        url: "api/session",
        dataType: "html"
    }).done(function( msg ) {
        alert( "Cleared" );
        if(do_refresh){
            refresh();
        }
    });
}

function clear_last_watch(func){
    $.ajax({
        type: "DELETE",
        url: "api/stacky/watch",
        dataType: "html"
    }).done(function( msg ) {
        if(func){
            func()
        }
    });
}

function stacky_watch(){

    $.ajax({
        type: "GET",
        url: "api/stacky/watch",
        dataType: "html"
    }).done(function( msg ) {
            $('#watch_table tbody').prepend(msg);
            $('#watch_table tbody').children("tr:gt(30)").remove()
        });

}

function start_watch(){
    window.setInterval(stacky_watch, 5000);
}

function refresh(){
    document.location.reload()
}