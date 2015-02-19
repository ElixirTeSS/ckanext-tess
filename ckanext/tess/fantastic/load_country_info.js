"use strict";

ckan.module('load_country_info', function ($, _) {
  return {
    initialize: function () {

        var country_code = this.options.country_code;
        var content = 'Wooo, this is CC!'.replace('CC', this.options.country_code);
        this.el.popover({content: content,
                        title: this.options.title,
                        trigger: 'hover'});
    }
  };
});
