'use strict';   // See note about 'use strict'; below

var app = angular.module('kdmManager', ['ngRoute',]);



app.controller('globalController', function($scope, $http) {
    $scope.registerModalDiv = function (modal_button_id, modal_div_id) {
        var btn = document.getElementById(modal_button_id);
        var modal = document.getElementById(modal_div_id);

        btn.onclick = function(b) {b.preventDefault(); modal.style.display = "block";}
        window.onclick = function(event) {if (event.target == modal) {modal.style.display = "none";}}
    };
});

app.controller("containerController", function($scope) {
});

app.controller("survivorNotesController", function($scope) {
    $scope.notes = [];
    $scope.formData = {};
    $scope.addNote = function (asset_id) {
        $scope.errortext = "";
        if (!$scope.note) {return;}
        if ($scope.notes.indexOf($scope.note) == -1) {
            $scope.notes.splice(0, 0, $scope.note);
//            $scope.notes.push($scope.note);
        } else {
            $scope.errortext = "The epithet has already been added!";
        };
        var http = new XMLHttpRequest();
        http.open("POST", "/", true);
        http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        var params = "add_survivor_note=" + $scope.note + "&modify=survivor&asset_id=" + asset_id
        http.send(params);
        $('#saved_dialog').fadeIn(200)
        $('#saved_dialog').show();
        $('#saved_dialog').fadeOut(1500)
    };

    $scope.removeNote = function (x, asset_id) {
        $scope.errortext = "";
        var rmNote = $scope.notes[x];
        $scope.notes.splice(x, 1);

        var http = new XMLHttpRequest();
        http.open("POST", "/", true);
        http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        var params = "rm_survivor_note=" + rmNote + "&modify=survivor&asset_id=" + asset_id
        http.send(params);
        $('#saved_dialog').fadeIn(200)
        $('#saved_dialog').show();
        $('#saved_dialog').fadeOut(1500)

    };
});

app.controller("epithetController", function($scope) {
    $scope.epithets = [];
    $scope.formData = {};
    $scope.addItem = function (asset_id) {
        $scope.errortext = "";
        if (!$scope.addMe) {return;}
        if ($scope.epithets.indexOf($scope.addMe) == -1) {
            $scope.epithets.push($scope.addMe);
        } else {
            $scope.errortext = "The epithet has already been added!";
        };


        var http = new XMLHttpRequest();
        http.open("POST", "/", true);
        http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        var add_name = $scope.addMe.name;
        if (add_name == undefined) {var add_name = $scope.addMe};
        var params = "add_epithet=" + add_name + "&modify=survivor&asset_id=" + asset_id
        http.send(params);

        $('#saved_dialog').show();
        $('#saved_dialog').fadeOut(1500)
    }
    $scope.removeItem = function (x, asset_id) {
        $scope.errortext = "";
        var removedEpithet = $scope.epithets[x];
        $scope.epithets.splice(x, 1);
        var http = new XMLHttpRequest();
        http.open("POST", "/", true);
        http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        var rm_name = removedEpithet.name;
        if (rm_name == undefined) {var rm_name = removedEpithet};
        var params = "remove_epithet=" + rm_name + "&modify=survivor&asset_id=" + asset_id;
        http.send(params);

        $('#saved_dialog').show();
        $('#saved_dialog').fadeOut(1500)

    }
});

// generic survivor attrib update sans page refresh
function updateAssetAttrib(source_input, collection, asset_id) {
//    window.alert(source_input + "id=" + source_input.id);

    // a little idiot-proofing for Yours Truly
    if (source_input.hasAttribute('id') != true) {window.alert("Trigger element has no id!")};

    var attrib_key = document.getElementById(source_input.id).name;
    var new_value = document.getElementById(source_input.id).value;

//    window.alert(attrib_key + " - " + new_value);

    // strikethrough for p.survivor_sheet_fighting_art_elements
    if (source_input.id == 'survivor_sheet_cannot_use_fighting_arts' ) {
        if (source_input.checked == true) {
            var x = document.getElementsByClassName("survivor_sheet_fighting_art");
            var i;
            for (i = 0; i < x.length; i++) {
                var struck = x[i];
                x[i].style.setProperty("text-decoration", "line-through");
                };
            } else {
            var x = document.getElementsByClassName("survivor_sheet_fighting_art");
            var i;
            for (i = 0; i < x.length; i++) {
                var struck = x[i];
                x[i].style.removeProperty("text-decoration", "line-through");
                };
        };
    };

    // emphasis effect for font.survival_action_emphasize
    if (source_input.id == 'cannot_spend_survival' ) {
        if (source_input.checked == true) {
            var x = document.getElementsByClassName("survival_action_available");
            var i;
            for (i = 0; i < x.length; i++) {
                x[i].style.removeProperty('font-weight', 'bold');
                x[i].style.removeProperty('color', '#000');
                x[i].classList.remove('survival_action_emphasize');
            };
            } else {
            var x = document.getElementsByClassName("survival_action_available");
            var i;
            for (i = 0; i < x.length; i++) {
                x[i].style.setProperty('font-weight', 'bold');
                x[i].style.setProperty('color', '#000');
            };
        };
    };


    var http = new XMLHttpRequest();
    http.open("POST", "/", true);
    http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    var params = attrib_key + "=" + new_value + "&modify=" + collection +"&asset_id=" + asset_id + "&norefresh=True";
    http.send(params);

    $('#saved_dialog').show();
    $('#saved_dialog').fadeOut(1500)

};

// burger sidenav
function openNav() {
    document.getElementById("mySidenav").style.width = '65%';
}
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}


// close modal windows from a span
function closeModal(modal_div_id) {
    var modal = document.getElementById(modal_div_id);
    modal.style.display = "none";
}
