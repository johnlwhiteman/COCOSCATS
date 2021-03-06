"use strict";
$(document).ready(function() {
    var projectID = $("#csProjectID").text().trim()
    $.ajax({
    type: "POST",
    url: "/Api/GetProject/" + projectID,
    contentType: "application/json; charset=utf-8",
    success: function(response) {
        if (response["Error"]) {
            handleError(response["Message"]);
        } else {
            var L1L2 = response["L1L2"]
            L1L2 = L1L2.replace(/{/g,"<span class=\"csL2\">{", L1L2);
            L1L2 = L1L2.replace(/}/g,"</span>}", L1L2);
            $("#csTitle").html(response["Title"]);
            $("#csDescription").html(response["Description"]);
            $("#csL1L2").html(L1L2);
            $("#csL1").html(response["L1"]);
            $("#csL2").html(response["L2"]);
            var wordCnt = response["VocabularyParsed"].length;
            if (wordCnt < 1) {
                return;
            }
            var html = "<table align=\"center\">\n<tr>\n";
            html += "<th>L1</th><th>L2</th><th>PoS</th><th>Count</th>\n";
            for (var i = 0; i < wordCnt; i++) {
                var word = response["VocabularyParsed"][i];
                html += "<tr>\n";
                html += "<td>" + word["L1"] + "</td>\n";
                html += "<td id=\"#" + word["L2"] + "\">" + word["L2"] + "</td>\n";
                html += "<td>" + word["Pos"] + "</td>\n";
                html += "<td align=\"center\">" + word["Cnt"] + "</td>\n";
                html += "</tr>\n";
            }
            html += "</table>\n";
            $("#csVocabulary").html("<pre>" + html + "</pre>");
        }
    },
    error: function(response, txtStatus, errMsg) {
        handleError(errMsg);
    }
});


























});