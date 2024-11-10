let timerValue = 0;  // Initialize timer value

window.onload = function() {
    // Log JS status to console
    console.log("JS Running");

    // Set chat window height based on initial element height
    var heightY = document.getElementById("ss-chat").offsetHeight;
    document.getElementById("ss-chat").style.height = heightY + "px";

    // Start timer update every second
    setInterval(updateTimer, 1000);

    // For Demo Purposes
    newChat("p", "Session Start", 0);
    newChat("i", "Cooking Cream Appeared", 23);
    newChat("i", "Vinegar Appeared", 45);
    newChat("p", "Cutting", 47);
    newChat("i", "Tomato Appeared", 52);
    newChat("i", "Cucumber Appeared", 67);
    newChat("c", "Be careful, you are cutting the pieces too large", 73);
    newChat("p", "Cooking", 87);
    newChat("i", "Tomato Appeared", 90);
    newChat("i", "Tomato Appeared", 90);
    newChat("c", "Two tomatoes may not be enough for you to gain sufficient calories", 90);
    newChat("i", "Potato Appeared", 91);
    newChat("c", "The potato is unpeeled, you should peel it to remove dirt", 91);
    newChat("p", "Session End", 232);
}

// Function to increment and display the timer
function updateTimer() {
    timerValue++;
    document.getElementById("se-time").children[1].textContent = timerValue;
}

// Function to add a new chat element based on type and content
function newChat(type, content, time) {
    var chatElm = document.getElementById("ss-default").cloneNode(true);
    chatElm.id = "";

    // Set CSS class and label based on type
    chatElm.className = "ss-box";
    if (type == "i") {
        chatElm.className += " ssc-item";
        chatElm.children[0].innerHTML = "ITEM";
    } else if (type == "p") {
        chatElm.className += " ssc-phase";
        chatElm.children[0].innerHTML = "PHASE";
    } else if (type == "a") {
        chatElm.className += " ssc-action";
        chatElm.children[0].innerHTML = "ACTION";
    } else {
        chatElm.className += " ssc-comm";
        chatElm.children[0].innerHTML = "COMMENT";
    }

    // Add timer value to label
    chatElm.children[0].innerHTML += " (" + String(time) + " SECONDS)";

    // Set content and display new chat element
    chatElm.children[1].innerHTML = content;
    chatElm.style.display = "block";
  
    // Append new chat to chat container and auto-scroll to bottom
    document.getElementById("ss-chat").append(chatElm);
    document.getElementById("ss-chat").scrollTop = document.getElementById("ss-chat").scrollHeight;
}