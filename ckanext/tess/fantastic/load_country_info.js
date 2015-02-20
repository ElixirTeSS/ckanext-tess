"use strict";

ckan.module('load_country_info', function ($, _) {
  return {
    initialize: function () {
        var selected = $('#cc option:selected');
        var selected_country_code = selected.attr('id');
        var selected_country_name = selected.attr('data-module-countryname');
        $('#country_name').val(selected_country_name);
        $('#flag').attr('src', "/images/node_flags/" + selected_country_code + ".png");
        //var country_code = this.options.country_code;
        //var country_name = this.options.countryname;
        //console.log('country code: ' + country_code);
        //console.log('country name: ' + country_name);
        this.el.on('click', this._onSelect);
    },
    _onSelect: function(event) {
        var selected = $('#cc option:selected');
        var selected_country_code = selected.attr('id');
        var selected_country_name = selected.attr('data-module-countryname');
        $('#country_name').val(selected_country_name);
        $('#flag').attr('src', "/images/node_flags/" + selected_country_code + ".png");
    }
  };
});
