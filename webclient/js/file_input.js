var app = angular.module('nuzzleClient')

app.directive('cpFileInput', ['$parse', function($parse) {
    return {
        restrict: 'EA', 
        template: '<input type="file">',
        replace: true,
        link: function(scope, element, attrs) {
            var modelGet = $parse(attrs.cpFileInput)
            var modelSet = modelGet.assign
            var onChange = $parse(attrs.onChange)

            element.bind('change', function() {
                scope.$apply(function() {
                    modelSet(scope, element[0].files[0])
                    onChange(scope)
                })
            })
        }
    }
}])
