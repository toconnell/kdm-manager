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
        var params = "add_epithet=" + $scope.addMe + "&modify=survivor&asset_id=" + asset_id
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
        var params = "remove_epithet=" + removedEpithet + "&modify=survivor&asset_id=" + asset_id;
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

    var http = new XMLHttpRequest();
    http.open("POST", "/", true);
    http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    var params = attrib_key + "=" + new_value + "&modify=" + collection +"&asset_id=" + asset_id;
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
