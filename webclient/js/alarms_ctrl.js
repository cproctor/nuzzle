var app = angular.module('nuzzleClient')

app.controller('alarmsCtrl', ['nuzzleApi', '$scope', function(nuzzleApi, $scope) {
    $scope.createAlarm = function() {
        var alarm = {
            time: $scope.newAlarm.time.utc().format("YYYY-MM-DD HH:mm:ss"),
            owner: USER,
            creator: USER,
            message_source: PARTNER
        }
        nuzzleApi.createAlarm(alarm, USER).success($scope.sync)
    }
    $scope.cancelAlarm = function(id) {
        nuzzleApi.cancelAlarm(USER, id).success($scope.sync)
    }
    $scope.updateAlarm = function(time) {
        $scope.newAlarm.time = time
    }
    $scope.sync = function() {
        nuzzleApi.getAlarms(USER).success(function(alarms) {
            $scope.alarms = alarms
        })
    }
    $scope.resetAlarm = function() {
        $scope.newAlarm = {
            time: moment().add(8, 'h')
        }
    }
    $scope.resetAlarm()
    $scope.sync()
}])
