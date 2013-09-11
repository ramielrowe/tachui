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

var watch_service = 'nova'

function stacky_watch(){

    $.ajax({
        type: "GET",
        url: "api/stacky/watch/"+watch_service,
        dataType: "html"
    }).done(function( msg ) {
            var watch_table = $('#watch_table tbody')
            watch_table.prepend(msg);
            watch_table.children("tr:gt(60)").remove()
        });

}

var watch_interval_id = 0;

function start_watch(){
    var service = $('#watch_form_service').val().trim();
    if(watch_service != service){
        clear_last_watch();
    }
    watch_service = service;
    if(watch_interval_id != 0){
        window.clearInterval(watch_interval_id);
    }
    watch_interval_id = window.setInterval(stacky_watch, 5000);
}

function stop_watch(){
    if(watch_interval_id != 0){
        window.clearInterval(watch_interval_id);
        watch_interval_id = 0;
    }
}

function refresh(){
    document.location.reload()
}

function toggle_watch_size(){
    $('#watch_table_container').toggleClass('expanded')
}

function do_search_args(service, field, value, limit){
    limit = limit || 'none';
    $("#search_progress").show();
    field = field.trim();
    value = value.trim();
    data = {'field': field, 'value': value};
    if(limit != 'none'){
        data['limit'] = limit;
    }
    var async = $.ajax({
        type: "GET",
        url: "api/stacky/search/"+service,
        data: data,
        dataType: "html"
    });
    async.done(function( msg ) {
        $("#search_progress").hide();
        var search_table = $('#search_table tbody');
        search_table.html(msg)
    });
    async.fail(function( msg ){
        $("#search_progress").hide();
    });
}

function do_search(){
    var service = $('#search_form_service').val().trim();
    var field = $('#search_form_field').val().trim();
    var value = $('#search_form_value').val().trim();
    var limit = $('#search_form_limit').val().trim();
    do_search_args(service, field, value, limit);
}

function close_show(loc, id){
    $("#s_"+loc+"_"+id+"_show").remove()
}

function show_event(loc, service, id){
    $("#search_progress").show();
    var async = $.ajax({
        type: "GET",
        url: "api/stacky/show/"+loc+"/"+service+"/"+id,
        dataType: "html"
    });
    async.done(function( msg ) {
        $("#search_progress").hide();
        var row = $('#s_'+loc+'_'+id);
        row.after(msg)
        $("html, body").animate({ scrollTop: $('#s_'+loc+'_'+id+'_show').offset().top - 75 }, 500);
    });
    async.fail(function( msg ){
        $("#search_progress").hide();
    });
}