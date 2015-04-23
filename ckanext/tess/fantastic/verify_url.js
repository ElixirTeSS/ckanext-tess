
/*
A method that checks whether values of elements with given ids (input fields)
start with 'http(s)://' or 'https://' and appends 'http://' if not.
You can pass any number of arguments, making sure they represent the element ids.
 */
function check_url_starts_with_http(){
    // Loop though all the passed arguments (representing ids of input elements)
    for (var i = 0; i < arguments.length; i++) {
        var elements = $("[id^="+arguments[i]+"]"); // Get all elements which id starts with a given argument
        elements.each(function(){
            var value = this.value.trim();
            if (value.toLowerCase().indexOf("file:") == 0){ // this is a local file URL - skip
                return true; // equivalent of continue!!!
            }
            if (value.toLowerCase().indexOf("http") != 0){
                this.value = 'http://' + value;
            }
        });
    }
    return true;
}
