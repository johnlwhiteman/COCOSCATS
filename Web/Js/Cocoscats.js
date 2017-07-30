"use strict";
$(document).ready(function() {

    function handleError(errMsg) {
        $("#csErrMsg").html(errMsg);
    }

    $("#editorReset").click( function() {
        window.location.href="/Reset";
    });

    $("#editorSave").click( function() {
        $.ajax({
            type: "POST",
            url: "/" + $("#csNavTitle").text() + "/Save",
            data: {Content: $("#csContent").val()},
            contentType: "application/json; charset=utf-8",
            success: function(response) {
                $("#csCfgMsg").html('<span class="csOkMsg">' + response + '</span>');
                setTimeout('$("#csCfgMsg").html("&nbsp;");', 3000);
            },
            error: function(response, txtStatus, errMsg) {
                $("#cfgMsg").html('<span class="csErrMsg">Save failed: ' + errMsg + '</span>');
            }
        });
    });

});