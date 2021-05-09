var currentTab = 0;
showTab(currentTab);
console.log(currentTab);
function showTab(n){
    var x = document.getElementsByClassName("tab");
    // show the current tab
    x[n].style.display = "block";

    // adjust the Back button
    if (n==0){
        document.getElementById("bckBtn").style.display = "none";
    }
    else{
        document.getElementById("bckBtn").style.display = "inline";
    }

    // adjust the Next button
    if (n == (x.length - 1)){
        document.getElementById("nxtBtn").style.innerHTML = "Submit";
    }
    else{
        document.getElementById("nxtBtn").style.innerHTML = "Next";
    }

    // call function to fix the "Step" at the bottom of the form
    fixStep(n)

}

function nextPrev(formname, n){
    // Display the correct tab
    var x = document.getElementsByClassName("tab");

    // Exit function if any of the field in current tab is invalid
    if (n == 1 && !valForm()) return false;

    // Hide current tab
    x[currentTab].style.display = "none";

    // Increase/Decrease current tab by 1
    currentTab += 1;

    // End of form
    if (currentTab >= x.length){
        document.getElementById(formname).onsubmit();
        return false;
    }
}

function valForm(){
    var x = document.getElementsByClassName("tab");
    var y = x[currentTab].getElementsByTagName("input");
    var valid = true;
    // loop to check every input field in current tab
    for (let i = 0; i < y.length; i++){
        // if a field is empty
        if (y[i].value == ''){
            // add an "invalid" class to the field
            y[i].className += "invalid";

            // set current valid status to false
            valid = false;
        }
    }
    if (valid){
        document.getElementsByClassName("step")[currentTab].className += " finish"
    }
    return valid;
}

function fixStep(n){
    var j = document.getElementsByClassName("step");

    // Remove class "active" frm all steps
    for (let i=0; i< j.length; i++){
        j[i].className = j[i].className.replace(" active", "");
    }

    // add " active" to current step/tab
    x[n].className += " active";
}