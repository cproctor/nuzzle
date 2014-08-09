SERVER = 'http://localhost:6543'
USER = 'chris'
PARTNER = 'zuz'

var app = angular.module('nuzzleClient', [])

app.controller('nuzzleController', function($scope) {
    $scope.nav = 'alarms'
})
