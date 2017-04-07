// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

require(["jquery", "jhapi"], function ($, JHAPI) {
    "use strict";
    
    var base_url = window.jhdata.base_url;
    var user = window.jhdata.user;
    var api = new JHAPI(base_url);
    
    $("#stop").click(function () {
        $("#wait").show();
        $("#start").hide();
        $("#stop").hide();
        api.stop_server(user, {
            success: function () {
                setTimeout(function() {
                    window.location.reload();
                }, 2000);
            }
        });
    });
    
});
