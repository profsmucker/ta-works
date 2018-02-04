$(document).ready(function() {
  $( ".number" ).on( "click", function() {
    if($( ".number:checked" ).length > 3)
    {
      $('#btn').prop('disabled', false);
    }
    else
    {
      $('#btn').prop('disabled', true);
    }
  });

  // hide all the inital reason inputs
  function hideInputs() {
      $(".reason_class").hide();
  }
  hideInputs();

  // listener for preference, creates a reason button if the rating is greater than 0
  $(".middle").each(function(i, j){
    $(j).find('.pref_class').on('change', function(){
      var val = $(j).find('.pref_class').val();
      // check for rating greater than 0
      if (val > 0) {
        // make the button if it doesn't exist
        if ($(j).find('.input_button').length == 0) {
          $(j).append(createReasonButton())
        }
      }
      // remove created button if rating reflects no longer interested in teaching the course
      // note: if previously rated 2, entered a reason and then later entered 0, the reason will
      // still save in the database.
      else {
        $(j).find('.input_button').remove();
      }
    })
  });

  // this is similar to a button click listener to prompt the user to enter a reason
  function btnClick(e){
    // remove the default submit behaviour, without it causes a bug to auto submit the form
    e.preventDefault()
    var reason = $(this).parent().find('.reason_class').val()
    // error handling to make sure use input doesn't exceed 255 characters
    reason = prompt("Please enter your reason for applying to TA this course. (255 character limit)", reason);
    while (reason.length > 255) {
      reason = prompt(reason.length - 255 + " characters over the limit. (255 character limit)", reason);
    }
    $(this).parent().find('.reason_class').val(reason);
  };

  // create sthe enter reason button
  function createReasonButton() {
    return $('<button/>', {
      text: 'Enter Reason',
      class: 'input_button',
      click: btnClick
    });
  }
});
