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

function sumTA() {
	var table = document.getElementById("numberTAs");
	var row = table.rows.length;
	var count;
	for (var i = 1; i < row; i++){
		var input1 = table.rows[i].cells[5].children[0].value;
		var input2 = table.rows[i].cells[6].children[0].value;
		var input3 = table.rows[i].cells[7].children[0].value;
		var input4 = table.rows[i].cells[8].children[0].value;
		var sum = Number(input1)+0.75*Number(input2)+0.5*Number(input3)+0.25*Number(input4);
		table.rows[i].cells[9].children[0].value = sum;
	}
}

function noEnter() {
  return !(window.event && window.event.keyCode == 13);
}
