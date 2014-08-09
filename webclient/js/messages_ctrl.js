var app = angular.module('nuzzleClient')

app.controller('messagesCtrl', ['nuzzleApi', 'cpFileReader', '$sce', '$scope', function(nuzzleApi, cpFileReader, $sce, $scope) {

    $scope.sync = function() {
        var trustUrls = function(messages) {
            _.each(messages, function(message) {
                message.url = $sce.trustAsResourceUrl(message.url)
            })
        }
        nuzzleApi.getMessages(USER).success(function(messages) {
            trustUrls(messages)
            $scope.messages = messages
        })
        nuzzleApi.getQueuedMessages(USER).success(function(messages) {
            trustUrls(messages)
            $scope.queue = messages
        })
    }
    $scope.createMessage = function() {
        var message = {
            name: $scope.newMessage.name,
            owner: USER,
            file: $scope.newMessage.base64File
        }
        nuzzleApi.createMessage(message, USER)
            .then($scope.sync)
            .then($scope.resetMessage)
    }

    $scope.deleteMessage = function(mId) {
        nuzzleApi.deleteMessage(USER, mId).success($scope.sync)
    }

    $scope.queueMessage = function(mId, position) {
        nuzzleApi.queueMessage(USER, mId, position).success($scope.sync)
    }

    $scope.unqueueMessage = function(position) {
        nuzzleApi.removeFromQueue(USER, position).success($scope.sync)
    }
    $scope.changeQueuePosition = function(mId, oldPos, change) {
        nuzzleApi.removeFromQueue(USER, oldPos)
            .then(function() {
                return nuzzleApi.queueMessage(USER, mId, oldPos + change)
            })
            .then($scope.sync)
    }

    $scope.readFile = function() {
        if ($scope.newMessage.file) {
            if ($scope.newMessage.file.type == 'audio/mp3') {
                $scope.newMessage.error = ""
                cpFileReader.readAsBinaryString($scope.newMessage.file, $scope)
                    .then(function(result) {
                        $scope.newMessage.working = false
                        $scope.newMessage.ready = true
                        $scope.newMessage.base64File = btoa(result)
                    })
            } else {
                $scope.newMessage.error = "You can only upload mp3 files. Please choose a different file."
            }
        }
    }

    $scope.resetMessage = function() {
        $scope.newMessage = {
            valid: false
        }
    }

    var validateMessage = function() {
        $scope.newMessage.valid = !!$scope.newMessage.name && !!$scope.newMessage.base64File
    }

    $scope.$watch('newMessage.name', validateMessage)
    $scope.$watch('newMessage.base64File', validateMessage)

    $scope.sync()
    $scope.resetMessage()
}])
