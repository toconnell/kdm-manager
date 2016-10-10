'use strict';   // See note about 'use strict'; below

var myApp = angular.module('kdmManager', ['ngRoute',]);


myApp.controller('globalController', function($scope, $http) {});

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
