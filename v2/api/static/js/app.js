'use strict';   // See note about 'use strict'; below

var myApp = angular.module('theWatcher', ['ngRoute',]);

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

myApp.config(
    ['$routeProvider',
     function($routeProvider) {
         $routeProvider.
             when('/', {
                 templateUrl: '/static/partials/index.html',
             }).
             when('/about', {
                 templateUrl: '../static/partials/about.html',
             }).
             otherwise({
                 redirectTo: '/'
             });
        }
    ]
);
