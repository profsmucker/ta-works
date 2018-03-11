$(document).ready(function() {
  var currentFormAlgo;
  var currentFormRanking;
  var currentFormStudentApp;
  var currentFormCourseUpload;

  $( "#dialog-confirm" ).dialog({
      resizable: false,
      autoOpen: false,
      modal: true,
      closeOnEscape: true,
      position: {
         my: "center bottom",
         at: "center center",
         of: $("#algo-run")
      },
      buttons: {
          "Yes": function() {
              $( this ).dialog( "close" );
              currentFormAlgo.append('<input type="hidden" name="algo_run" value="Solve model"/>');
              currentFormAlgo.submit();
          },
          "No": function() {
              $( this ).dialog( "close" );
          }
      }
  });  
  $( ".submitButton2Popup" ).click(function() {
      currentFormAlgo = $(this).closest( "form" );
      $( "#dialog-confirm" ).dialog( "open" );
      return false;
  });

  $( "#email-confirm" ).dialog({
      resizable: false,
      autoOpen: false,
      modal: true,
      closeOnEscape: true,
      position: {
         my: "center bottom",
         at: "center center",
         of: $("#ranking")
      },
      buttons: {
          "Yes": function() {
              $( this ).dialog( "close" );
              currentFormRanking.append('<input type="hidden" name="Upload" value="Send Out Ranking Links"/>');
              currentFormRanking.submit();
          },
          "No": function() {
              $( this ).dialog( "close" );
          }
      }
  });  
  $( ".emailButtonPopup" ).click(function() {
      currentFormRanking = $(this).closest( "form" );
      $( "#email-confirm" ).dialog( "open" );
      return false;
  });

  $( "#app-confirm" ).dialog({
      resizable: false,
      autoOpen: false,
      modal: true,
      closeOnEscape: true,
      position: {
         my: "center bottom",
         at: "center top",
         of: $("#confirm-boxes")
      },
      buttons: {
        "Yes": function(){
          $( this ).dialog ( "close" );
          currentFormStudentApp.append('<input type="hidden" name="AppConfirm" value="Submit">');
          currentFormStudentApp.submit();
        },
        "No": function() {
          $( this ).dialog( "close" );
        }
      }
  });
  $( ".applicationButtonPopup" ).click(function() {
    currentFormStudentApp = $(this).closest( "form" );
    $( "#app-confirm" ).dialog( "open" );
    return false;
  });

  $( "#course-confirm" ).dialog({
      resizable: false,
      autoOpen: false,
      modal: true,
      closeOnEscape: true,
      buttons: {
        "Yes": function(){
          $( this ).dialog ( "close" );
          currentFormCourseUpload.append('<input type="hidden" name="courseUpload" value="Upload">');
          currentFormCourseUpload.submit();
        },
        "No": function() {
          $( this ).dialog( "close" );
        }
      }
  });
  $( ".courseUploadButton" ).click(function() {
    currentFormCourseUpload = $(this).closest( "form" );
    $( "#course-confirm" ).dialog( "open" );
    return false;
  });

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
          $(j).append(createReasonButton());
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
    e.preventDefault();
    var currentContext = $(this).parent();
    // makes a temporary dialog for taking user input
    $('<div><p>Please indicate why you are fit for teaching this course. Include any relevant past experience in your answer. <br>(1500 character limit)</p><textarea maxlength=1500 id=tempBox ></textarea></div>').dialog({
      modal: true,
      height: 615,
      width: 750,
      resizable: false,
      draggable: false,
      closeOnEscape: false,
      title: "Enter your reason below.",
      buttons: {
        'OK': function () {
          currentContext.find('.reason_class').val($('#tempBox').val());
          $(this).dialog("destroy");
          $(this).remove();
        },
        'Cancel': function () {
          $(this).dialog("destroy");
          $(this).remove();
        }
      }
    });
    $('#tempBox').val(currentContext.find('.reason_class').val());
  };

  // creates the enter reason button
  function createReasonButton() {
    return $('<button/>', {
      text: 'Enter Reason',
      class: 'input_button',
      click: btnClick
    });
  }

  $(".pref_class").trigger('change');
  $("#applicantTable").tablesorter(); 
});
