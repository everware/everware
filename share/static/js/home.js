// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

require(["jquery", "jhapi"], function ($, JHAPI) {
    "use strict";
    
    var base_url = window.jhdata.base_url;
    var user = window.jhdata.user;
    var api = new JHAPI(base_url);

    var id = setInterval(function () {
        window.location.reload();
    }, 5000);
    
    $("#stop").click(function () {
        $("#wait").show();
        $("#start").hide();
        api.stop_server(user, {
            success: function () {
                /*setTimeout(function() {
                    window.location.reload();
                }, 3000);*/
            }
        });
    });
    
});
