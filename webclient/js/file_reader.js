var app = angular.module('nuzzleClient')

// http://odetocode.com/blogs/scott/archive/2013/07/03/building-a-filereader-service-for-angularjs-the-service.aspx
// In this module we create a FileReader object whose event callbacks close over references to a promise.
// The callbacks resolve the promise appropriately, effectively mapping the native events of the FileReader into
// the promise-based Angular environment.
app.factory('cpFileReader', ['$q', function($q) {

    var onLoad = function(reader, deferred, scope) {
        return function() {
            scope.$apply(function() {
                deferred.resolve(reader.result)
            })
        }
    }

    var onError = function(reader, deferred, scope) {
        return function() {
            scope.$apply(function() {
                deferred.reject(reader.result)
            })
        }
    }

    var onProgress = function(reader, scope) {
        return function(evt) {
            scope.$broadcast("fileProgress", {
                total: evt.total,
                loaded: evt.loaded
            })
        }
    }

    var getReader = function(deferred, scope) {
        var reader = new FileReader()
        reader.onload = onLoad(reader, deferred, scope)
        reader.onerror = onError(reader, deferred, scope)
        reader.onprogress = onProgress(reader, scope)
        return reader
    }

    var readAsDataUrl = function(file, scope) {
        var deferred = $q.defer()
        var reader = getReader(deferred, scope)
        reader.readAsDataURL(file)
        return deferred.promise
    }

    var readAsBinaryString = function(file, scope) {
        var deferred = $q.defer()
        var reader = getReader(deferred, scope)
        reader.readAsBinaryString(file)
        return deferred.promise
    }
    
    return {
        readAsDataUrl: readAsDataUrl,
        readAsBinaryString: readAsBinaryString
    }
}])
