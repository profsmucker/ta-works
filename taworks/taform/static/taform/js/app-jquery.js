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
});
