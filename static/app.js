angular.module('MusicShare', [])
	.directive('myAudio', function() {
		return function(scope, element, attrs) {
			scope.$watch(element[0].ended, function(){
				console.log(element[0].ended)
				var next = element[0].ended

			
			});
		}
});