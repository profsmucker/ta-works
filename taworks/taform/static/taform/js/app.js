//Function to not let users post data twice when clicking back
function noBack() {
    window.history.forward();
}
//Function to make the student visa expiry date input hidden unless citizenship=student visa
function visaFunction() {
	var visaSelect = document.getElementById("id_citizenship");
	var strVisaSelect = visaSelect.options[visaSelect.selectedIndex].text;
	if(strVisaSelect == "Student Visa"){
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