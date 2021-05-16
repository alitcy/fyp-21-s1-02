var text;
text = "";

var test = '';
// //test = "as the rental car rolled to a stop on the dark road, her fear increased by the moment.";                   // to be changed to generated sentence, i liked it when they brushed right up against the buildings north of the loop and i especially liked it when the buildings dropped away into that bombed-out squalor a little farther north.

var enteredText;
enteredText = [];

// Clear when window is loaded
window.onload = clearAll();

//Variables for dwell time
var timeTakenDwell;
timetakenDwell = 0;
var startDwellTime;
starDwelltTime = 0;
var stopDwellTime;
stopDwellTime = 0;
var recordDwellTime;
recordDwellTime = [];

//Variables for time taken
var timeTaken;
timeTake = 0;
var startTime;
startTime = 0;
var stopTime;
stopTime = 0;

//Variables for flight time
var startFlightTime;
startFlightTime = [];
var stopFlightTime;
stopFlightTime = [];
// var totalFlightTime;
// totalFlightTime = 0;
var checkFlight = false;        //to check if stop flight time is required

var numOfTimeTyped;
numOfTimeTyped = 0;

var checkTimeTakenStarted;
checkTimeTakenStarted = false;

var currentKey;

var preventBkSpTime = false; //to prevent time taken to press backspace to be saved in recordTime

var checkShift = false;

var checkCaps = false;

var originalSentence; //length of original sentence before/after any backspace

function timer(timer) {
    this.time = timer;
}

timer.prototype.getTime = function () {
    return this.time
};

// array to store the json strings (for recalibration/registration where user needs 10 attempts)
var resultsArray = [];

function keyDown(userEntry, e) {
    if (checkTimeTakenStarted == false) {
        var temp = new timer(Date.now());
        console.log(temp);
        startTime = temp.getTime();         // start time taken for whole sentence authentication
        checkTimeTakenStarted = true;
    }

    if (e.charCode == 8 || e.keyCode == 8)    //check for backspace, and dlt last element in time array
    {
        preventBkSpTime = true;
    }
    else if (e.keyCode == 16) {
        checkShift = true;
    }
    else if (e.keyCode == 20) {
        checkCaps = true;
    }
    else {
        var temp = new timer(Date.now());
        startDwellTime = temp.getTime();

        if (checkFlight == true) {
            if (document.getElementById(userEntry).value != null &&
                document.getElementById(userEntry).value.length == 0)         // if input empty, break if condition
            {
                checkFlight = false;
                stopFlightTime = [];
                startFlightTime = [];
            }
            else {
                var temp = new timer(Date.now());
                stopFlightTime.push(temp.getTime());
            }
        }
    }
}

function keyPress(e)                       //Record what was entered in the input
{
    currentKey = e;
    enteredText.push(currentKey.key);
    numOfTimeTyped++;
}


function keyUp(sentence, userEntry) {

    if (preventBkSpTime == false)   //check if backspace is entered
    {
        if (checkShift != true) {
            if (checkCaps != true) {
                var temp = new timer(Date.now());
                stopDwellTime = temp.getTime();
                timeTakenDwell = stopDwellTime - startDwellTime;
                stopDwellTime = 0;
                starDwelltTime = 0;
                recordDwellTime.push(timeTakenDwell);
                timeTakenDwell = 0;

                if (checkFlight == false) {
                    var temp = Date.now();
                    startFlightTime.push(temp);
                    checkFlight = true;
                }
                else {

                    console.log("Size of startFlight Array: " + startFlightTime.length);
                    console.log("Size of stopFlight Array: " + stopFlightTime.length);
                    var temp = Date.now();
                    startFlightTime.push(temp);
                    console.log("Size of startFlight Array after keyup: " + startFlightTime.length);
                    console.log("Size of stopFlight Array after keyup: " + stopFlightTime.length);
                }
            }
            else {
                checkCaps = false;
            }

        }
        else {
            checkShift = false;
        }

    }
    else 
    { 

        stopFlightTime.splice(-1);
        startFlightTime.splice(-1);
        startFlightTime.splice(-1);
        enteredText.splice(-1);
        recordDwellTime.splice(-1);

        // currentSentence = document.getElementById(userEntry).value.length;
        // var numberOfTimes = originalSentence - currentSentence;
        // console.log(numberOfTimes);

        // if (numberOfTimes == 1)
        // {
        //     stopFlightTime.splice(-1);
        //     startFlightTime.splice(-1);
        //     startFlightTime.splice(-1);
        //     enteredText.splice(-1);
        //     recordDwellTime.splice(-1);
        // }
        // else
        // {
        //     for (i = 1; i < numberOfTimes; i++)
        //     {
        //         stopFlightTime.splice(-1);
        //         enteredText.splice(-1);
        //         recordDwellTime.splice(-1);
        //     }

        //     for (i = 1; i < numberOfTimes+1; i++)
        //     {
        //         startFlightTime.splice(-1);
        //     }
        // }

        if (document.getElementById(userEntry).value.length != 0)         // if no input left, dont start FlightTime
        {
            var temp = Date.now();
            startFlightTime.push(temp);
        }
        else {
            checkFlight = false;
        }

        console.log("Size of startFlight Array after keyup: " + startFlightTime.length);
        console.log("Size of stopFlight Array after keyup: " + stopFlightTime.length);

        preventBkSpTime = false;

    }

    originalSentence = document.getElementById(userEntry).value.length;

    text = document.getElementById(userEntry).value; // user input
    test = document.getElementById(sentence).innerHTML; // generated sentence
    if (text.length == test.length)					// to check input value length if equal to test length
    {
        //Calculate total time taken
        var temp = new timer(Date.now());
        console.log(temp);
        stopTime = temp.getTime();
        timeTaken = stopTime - startTime;

    }
}

var totalDwellTimeArray;
totalDwellTimeArray = [];

var totalAccuracyArray;
totalAccuracyArray = [];

var totalWPMArray;
totalWPMArray = [];

var totalTimeTakenArray;
totalTimeTakenArray = [];

var totalFlightTimeTakenArray;
totalFlightTimeTakenArray = [];

var enteredTextArray;
enteredTextArray = [];

var counter;
counter = 0;

function clearAll(){
    //Clearing all the values
    startFlightTime = [];
    stopFlightTime = [];
    checkFlight = false;
    timeTaken = 0;
    totalDwellTime = 0;
    numOfTimeTyped = 0;
    totalFlightTime = 0;
    text = "";
    recordDwellTime = [];
    recordFlightTime = [];
    enteredText = [];
    totalDwellTimeArray = [];
    totalFlightTimeTakenArray = [];
    totalAccuracyArray = [];
    totalWPMArray = []
}
function calculateResults()                                             // Confirm button functionality, calculate total time taken
{
    if (test.localeCompare(text) == 0) {
        checkTimeTakenStarted = false;							// stop the Timetaken timer

        //to insert all individual values
        for (i = 0; i < recordDwellTime.length; i++) {
            totalDwellTimeArray.push(recordDwellTime[i]);
        }

        //calculate accuracy
        var accuracy;
        accuracy = (test.length / numOfTimeTyped) * 100;

        totalAccuracyArray.push(accuracy);

        // Calculate total flight time taken
        for (i = 0; i < stopFlightTime.length; i++) {
            var temp;
            temp = stopFlightTime[i] - startFlightTime[i];
            totalFlightTimeTakenArray.push(temp);
        }

        var numOfChar = parseFloat(enteredText.length / 5);                     //split generated sentence into words using space
        var timeTakenInSec = timeTaken / 1000;         // time taken in sec
        totalTimeTakenArray.push(timeTakenInSec);
        var timeTakenInMin = timeTaken / 60000;        // time taken in min
        var WPM = numOfChar / timeTakenInMin;        // calculate words per min

        enteredTextArray.push(enteredText);
        totalWPMArray.push(WPM);
        
        return true;
    }
    else{
        return false;
    }
}

function packObject(accuracy, wpm, dwell, flight){
    return (
        {
            'accuracy': accuracy,
                'wpm': wpm,
                'dwell': dwell,
                'flight': flight
        }
    )
}

function loginConfirm(form_id, hidden_id, e){
    e.preventDefault();
    let j_string = JSON.stringify('');
    let results = calculateResults();
    if (results === false){
        alert("Sentence entered does not match generated sentence. Please try again.")
    }
    else{ // success
        try{
            j_string = JSON.stringify(packObject(totalAccuracyArray[0], totalWPMArray[0], totalDwellTimeArray, totalFlightTimeTakenArray));
            document.getElementById(hidden_id).value = j_string;
        }
        catch (Error){
            console.log(Error.message);
            return false;
        }
        finally{
            document.getElementById(form_id).submit();
            clearAll();
        }
    }    
}
// array to store the json strings (*10 attempts) let resultsArray = [];

// counter variable
let habitCounter = 1;
function recalibrateAndRegister(textarea_id, instruction, nextBtn, SubmitBtn, e){
    e.preventDefault();
    // variables needed
    let j_string = JSON.stringify('');
    let results = false;
    let instruction_string = '';

    results = calculateResults();

    if (results === false){
        alert("Sentence entered does not match generated sentence. Please try again.");
    }
    else{
        j_string = packObject(totalAccuracyArray[0], totalWPMArray[0], totalDwellTimeArray, totalFlightTimeTakenArray);
        if(checkNaNValueInJSON(j_string) == true){
            alert("Please type in the box below the generated sentence.");
        }
        else{
            resultsArray.push(j_string); // store into array
            if (habitCounter === 10) {
                // need to do:
                // hide the "fake" submit button
                // replace with the new submit button
                // reset habitCounter = 1
                document.getElementById(nextBtn).style.display = 'none'; // remove the fake submit button
                document.getElementById(textarea_id).style.display = 'none'; // remove text area because no need to type anymore
                instruction_string = "Press the button below to complete your registration."
                document.getElementById(instruction).innerHTML = instruction_string; // change the instruction
                document.getElementById(SubmitBtn).style.display = 'block'; // show the actual submit button (submit & send to server side)
                habitCounter = 1;
            }
            else if (habitCounter<10){
                instruction_string = String(habitCounter+1) + "/10 attempt(s)";
                document.getElementById(instruction).innerHTML = instruction_string; // show attempt number
                habitCounter++; // increase count
            }
        }
        document.getElementById(textarea_id).value = ''; // reset the textarea
        clearAll(); // clear all the accuracy/wpm/dwell/flight global arrays
    }
}

function submitRecalAndRegArray(hidden_id, form_id, e){
    e.preventDefault();
    let j_string = JSON.stringify(resultsArray);
    document.getElementById(hidden_id).value = j_string;
    document.getElementById(form_id).submit();

}

function checkNaNValueInJSON(json) {
    for (key in json) {
        if (typeof (json[key]) === "object") {
            return checkNaNValueInJSON(json[key]);
        } else
            if (isNaN(json[key])){
                return true;
            }
        }
    return false;
}