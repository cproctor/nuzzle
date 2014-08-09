var app = angular.module('nuzzleClient')

app.controller('historyCtrl', ['nuzzleApi', '$scope', function(nuzzleApi, $scope) {
    $scope.plays = nuzzleApi.getMessageHistory(USER)
}])

