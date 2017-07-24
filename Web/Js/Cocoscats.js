"use strict";
$( document ).ready(function() {

    $("#editorReset").click( function() {
        window.location.href="/Reset";
    });

    $("#editorSave").click( function() {
        $.ajax({
            type: "POST",
            url: "/" + $("#navTitle").text() + "/Save",
            data: {Content: $("#content").val()},
            contentType: "application/json; charset=utf-8",
            success: function(response) {
                $("#cfgMsg").html('<span class="okMsg">' + response + '</span>');
                setTimeout('$("#cfgMsg").html("&nbsp;");', 3000);
            },
            error: function(response, txtStatus, errMsg) {
                $("#cfgMsg").html('<span class="errMsg">Save failed: ' + errMsg + '</span>');
            }
        });
    });

});