'use strict';

var app = angular.module('theWatcherDocs', []);

app.filter('trustedHTML', function($sce) {
     return $sce.trustAsHtml;
    }
);


app.controller('rootController', function($scope, $http) {

    $scope.objectKeys = Object.keys;

    $scope.init = function() {
        $http.get('/stat').then(
            function(result){
                $scope.stat = result.data;
                }
            );
        $http.get('/docs/get/json').then(
            function(result){
                $scope.docs = result.data;
            }
        );
        $http.get('/docs/get_sections/json').then(
            function(result){
                $scope.section_lookup = result.data;
            }
        );
    };


    $scope.init();


    $scope.toggleAboutBlock = function(){
        var e = document.getElementById('aboutBlock');
        e.classList.toggle('closed');
    };

    $scope.toggleNav = function(){
        document.getElementById("christianSideNav").classList.toggle('nav_open');
        document.getElementById("container").classList.toggle('nav_open');
    };

    $scope.scrollTo = function(target_element){
        var target = document.getElementById(target_element);
        target.scrollIntoView({behavior: 'smooth', block: 'nearest', inline: 'start'});
    };

});
