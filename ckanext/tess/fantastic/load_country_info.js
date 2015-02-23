"use strict";

ckan.module('load_country_info', function ($, _) {
  return {
    initialize: function () {
        var selected = $('#country_code option:selected');
        var selected_country_code = selected.attr('id');
        var selected_country_name = selected.attr('data-module-country_name');
        console.log('country code: ' + selected_country_code);
        console.log('country name: ' + selected_country_name);
        //SLUGIFICATE NAME
        var slug = selected_country_name;
        this.regexToHyphen = [ new RegExp('[ .:/_]', 'g'),
                      new RegExp('[^a-zA-Z0-9-_]', 'g'),
                      new RegExp('-+', 'g')];
        $.each(this.regexToHyphen, function(idx,regex) { slug = slug.replace(regex, '-'); });
        slug = slug.toLowerCase();
        //console.log(slug);
        $('#title').val(selected_country_name);
        $('#name').val(slug);
        $('#display_name').val(selected_country_name);
        $('#flag').attr('src', "/images/node_flags/" + selected_country_code + ".png");


        //var country_code = this.options.country_code;
        //var country_name = this.options.countryname;
        console.log('country code: ' + selected_country_code);
        console.log('country name: ' + selected_country_name);
        this.el.on('change', this._onChange);
    },
    _onChange: function(event) {
        var selected = $('#country_code option:selected');
        var selected_country_code = selected.attr('id');
        var selected_country_name = selected.attr('data-module-country_name');

        console.log('country code: ' + selected_country_code);
        console.log('country name: ' + selected_country_name);
        //SLUGIFICATE NAME
        var slug = selected_country_name;
        this.regexToHyphen = [ new RegExp('[ .:/_]', 'g'),
                      new RegExp('[^a-zA-Z0-9-_]', 'g'),
                      new RegExp('-+', 'g')];
        $.each(this.regexToHyphen, function(idx,regex) { slug = slug.replace(regex, '-'); });
        slug = slug.toLowerCase();
        //console.log(slug);
        $('#title').val(selected_country_name);
        $('#name').val(slug);
        $('#display_name').val(selected_country_name);
        $('#flag').attr('src', "/images/node_flags/" + selected_country_code + ".png");
    }
  };
});
