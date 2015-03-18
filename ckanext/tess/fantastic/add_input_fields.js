/**
 * Created by alex on 17/03/2015.
 */
/** Based on: http://www.sanwebe.com/2013/03/addremove-input-fields-dynamically-with-jquery */
/** jQuery to add input fields dynamically and stop when it reaches maximum. */

$(document).ready(function () {
    $('#addStaffMember').click(function (event) {
        $('<div/>', {
            'class' : 'staffMember', html: GetHtml()
        }).hide().appendTo('#extraStaffContainer').slideDown('slow');
    });
})

$(document).on('click', '#removeStaffMember', function(event) {
        $(event.target).parent('div').remove();
});

function GetHtml()
{
    //var len = $('.extraStaffMember').length;
    var $html = $('.extraStaffTemplate').clone();
    //$html.find('[name=staff_name]')[0].name="staff_name_" + (len+1);
    //$html.find('[name=staff_email]')[0].name="staff_email_" + (len+1);
    //$html.find('[name=staff_role]')[0].name="staff_role_" + (len+1);
    //$html.find('[name=staff_image]')[0].name="staff_image_" + (len+1);
    return $html.html();
}

// Create the JSON string from all staff (name, email, role)
// input fields and submit as hidden input named 'staff'
$('#node_form').submit(function(){ //listen for submit event

    var allStaffJSONObject = new Object();
    allStaffJSONObject.staff = []; // list of staff

    $('.staffMember').each(function(i, obj) {
        var staffJSONObject = new Object();
        staffJSONObject.name = $(this).find("input[name='staff_name']").val();
        staffJSONObject.email = $(this).find("input[name='staff_email']").val();
        staffJSONObject.role = $(this).find("input[name='staff_role']").val();
        // Add staff but only if al least one field is not empty
        if (staffJSONObject.name != '' || staffJSONObject.email != '' || staffJSONObject.role != '')
            allStaffJSONObject.staff.push(staffJSONObject);
    });

    var allStaffJSONString = JSON.stringify(allStaffJSONObject);

    // Create the 'staff' hidden input field and append to form
    $('<input>').attr({
        type: 'hidden',
        name: 'staff',
        value: allStaffJSONString
    }).appendTo($(this));
});