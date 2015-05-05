"use strict";

ckan.module('associate_event', function ($, _) {
    return {
        initialize: function() {
            $.proxyAll(this, /_on/);
            this.el.on('click', this._onclick);
        },
        _onclick: function (event) {

          $.proxyAll(this, /_on/);

            var data_dict = {
                "event_id": this.options.event_id,
                "event_url": this.options.event_url,
                "resource_id": this.options.resource_id
            }
            console.log(data_dict);
            $.ajax({
                type: 'POST',
                beforeSend: function (request) {
                    request.setRequestHeader("Authority", 'b8ec0537-efa2-4242-b01f-8219d3077311');
                    request.setRequestHeader("content-type", 'application/json');
                },
                url: 'http://localhost:5000/api/3/action/associate_event',
                data: JSON.stringify(data_dict),
                success: function (success) {
                    alert(JSON.stringify(success))
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    alert(xhr.responseText);
                }
            });
        }
    };
});

$(document).ready(function () {
    console.log('ready');
});
