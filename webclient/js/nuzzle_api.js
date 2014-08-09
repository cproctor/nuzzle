var app = angular.module('nuzzleClient')

app.service('nuzzleApi', ['$http', function($http) {
    this.createAlarm = function(alarm, user) {
        return $http.post(SERVER + '/api/v1/alarms/' + user, alarm)
    }
    this.cancelAlarm = function(user, alarmId) {
        return $http.delete(SERVER + '/api/v1/alarms/' + user + '/' + alarmId)
    }
    this.getAlarms = function(user) {
        return $http.get(SERVER + '/api/v1/alarms/' + user)
    }
    this.getMessages = function(user) {
        return $http.get(SERVER + '/api/v1/messages/' + user)
    }
    this.getQueuedMessages = function(user) {
        return $http.get(SERVER + '/api/v1/messages/' + user + '/queue')
    }
    this.queueMessage = function(user, messageId, position) {
        var apiCall = SERVER + '/api/v1/messages/' + user + '/queue'
        if (position !== undefined) 
            apiCall += '/' + position
        return $http.post(apiCall, {id: messageId})
    }
    this.removeFromQueue = function(user, position) {
        return $http.delete(SERVER + '/api/v1/messages/' + user + '/queue/' + position)
    }
    this.createMessage = function(message, user) {
        return $http.post(SERVER + '/api/v1/messages/' + user, message)
    }
    this.deleteMessage = function(user, messageId) {
        return $http.delete(SERVER + '/api/v1/messages/' + user + '/' + messageId)
    }
    this.getMessageHistory = function(user) {
        return $http.get(SERVER + '/api/v1/messages/' + user + '/history')
    }
}])
