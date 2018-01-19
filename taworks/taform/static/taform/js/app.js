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
//Function to make the student visa expiry date input hidden unless citizenship=student visa
function visaFunction() {
	var visaSelect = document.getElementById("id_citizenship");
	var strvisaSelect = visaSelect.options[visaSelect.selectedIndex].text;
	if(strvisaSelect == "Student Visa"){
		document.getElementById("expiryInput").hidden=false;
		document.getElementById("visaID").hidden=false;
		document.getElementById("expiryDate").hidden=false;
	}
	else{
		document.getElementById("expiryInput").hidden=true;
		document.getElementById("visaID").hidden=true;
		document.getElementById("expiryDate").hidden=true;
	}
}
