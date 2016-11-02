'use strict';   // See note about 'use strict'; below

var app = angular.module('kdmManager', ['ngRoute',]);

app.controller('globalController', function($scope, $http) {});



//myApp.config(
//    ['$routeProvider',
//     function($routeProvider) {
//         $routeProvider.
//             when('/', {
//                 templateUrl: '/static/partials/index.html',
//             }).
//             when('/about', {
//                 templateUrl: '../static/partials/about.html',
//             }).
//             otherwise({
//                 redirectTo: '/'
//             });
//        }
//    ]
//);
