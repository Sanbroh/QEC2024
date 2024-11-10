window.onload = function() {
    // Log JS status to console
    console.log("JS Running");

    // for (let i = 0; i < 4; i++) {
    //     var h = document.getElementsByClassName("s-cont")[i].offsetHeight;
    //     console.log(document.getElementsByClassName("s-cont")[i]);
    //     document.getElementsByClassName("s-cont")[i].style.height = h + "px !important";
    // }

    document.getElementById("s-o").innerHTML = scores[0];
    document.getElementById("s-i").innerHTML = scores[1];
    document.getElementById("s-r").innerHTML = scores[2];
    document.getElementById("s-g").innerHTML = scores[3];
}