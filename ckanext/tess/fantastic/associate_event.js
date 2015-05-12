"use strict";

ckan.module('event_association', function ($, _) {
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

            var key = this.options.key;

            $.ajax({
                type: 'POST',
                beforeSend: function (request) {
                    request.setRequestHeader("Authority", key);
                    request.setRequestHeader("content-type", 'application/json');
                },
                url: 'http://localhost:5000/api/3/action/' + this.options.action,
                data: JSON.stringify(data_dict),
                success: function (result_hash) {
                    console.log(result_hash)
                    if (result_hash['success'] == true) {
                        alert(JSON.stringify(result_hash['result']))
                        location.reload();
                    } else {
                        alert(result_hash['error']['message'])
                    }
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    alert(xhr.responseJSON['error']['message']);
                }
            });
        }
    };
});


$(document).ready(function () {
    console.log('ready');
});
