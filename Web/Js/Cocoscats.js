"use strict";
$(document).ready(function() {

    function handleError(errMsg) {
        $("#csErrMsg").html(errMsg);
    }

    $("#editorReset").click( function() {
        window.location.href="/Reset";
    });

    function viewxProject(projectID) {
        $.ajax({
            type: "POST",
            url: "/Api/GetProject/" + projectID,
            contentType: "application/json; charset=utf-8",
            success: function(response) {
                if (response["Error"]) {
                    handleError(response["Message"]);
                } else {
                    $("#csTitle").html("<h2>" + response["Title"] + "</h2>");
                    $("#csDescription").html(response["Description"]);
                    $("#csL1L2").html("<h2>L1L2</h2>" + response["L1L2"]);
                    $("#csL1").html("<h2>L1</h2>" + response["L1"]);
                    $("#csL2").html("<h2>L2</h2>" + response["L2"]);
                }
            },
            error: function(response, txtStatus, errMsg) {
                handleError(errMsg);
            }
        });
    }

    $("#editorSave").click( function() {
        $.ajax({
            type: "POST",
            url: "/" + $("#csNavTitle").text() + "/Save",
            data: {Content: $("#content").val()},
            contentType: "application/json; charset=utf-8",
            success: function(response) {
                $("#cfgMsg").html('<span class="csOkMsg">' + response + '</span>');
                setTimeout('$("#cfgMsg").html("&nbsp;");', 3000);
            },
            error: function(response, txtStatus, errMsg) {
                $("#cfgMsg").html('<span class="csErrMsg">Save failed: ' + errMsg + '</span>');
            }
        });
    });

});