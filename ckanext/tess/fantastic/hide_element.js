ckan.module('hide_element', function ($, _) {
    return {
        initialize: function() {
            $.proxyAll(this, /_on/);
            this.el.on('click', this._onclick);
        },
        _onclick: function (event) {
          $.proxyAll(this, /_on/);
            $('.' + this.options.hide_class).hide();
        }
    };
});
$(document).ready(function () {
    console.log('RADDDEE');
});
