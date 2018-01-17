//Function to run checkbox logic for disallowing "I Accept" without all disclosures marked first
function checkboxFunction() {
    if(document.getElementById("check1").checked == true && document.getElementById("check2").checked == true && document.getElementById("check3").checked == true && document.getElementById("check4").checked == true){
         document.getElementById("check5").disabled =! true;
    }
    else{
          document.getElementById("check5").disabled = true;
    }
}
//Function to not let users post data twice when clicking back
function noBack() {
    window.history.forward();
}
