'use strict';   // See note about 'use strict'; below

var myApp = angular.module('theWatcher', []);

myApp.controller('globalController', function($scope, $http) {
    "use strict";
    $scope.getSettings = function() {
    $http.get('settings.json').then(
        function(result){
            $scope.settings = result.data;
            }
        );
    };
    $scope.getSettings();
});
