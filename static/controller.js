'use strict';

/* Controllers */

function SongSearchCtrl($scope, $http, $document, $timeout){
	$scope.songsList = [];
	$scope.playList = [];
	$scope.songNumber = 0;
	$scope.loadedLists = [];
	$scope.error = new Object();
	$scope.logged = new Object();
	$scope.logged.loggedin = false;
	$scope.logged.show = false;
	$scope.logged.name = "";
	$scope.songSelection = false;
	$scope.playListBool = false;
	$scope.songBeingPlayed = 0;
	$scope.activeSong = false;
	
	var audio = $document.find('audio')[0]
	var fileInput = document.getElementById('fileInput')
	
	$scope.search = function(description) {
		$scope.transmit = description
		$http.post('/', description).success(function(data) {
			//console.log(data);
			if (data != "false") {	
				$scope.songs = data;
				$scope.songSelection = true;
			};
		});
	};
	
	$scope.addSong = function(aSong) {
		$scope.songsList.push(aSong);
		$scope.songNumber++;
		audio.autoplay = false
		if ($scope.songNumber == 1) {
			$scope.activeSong = $scope.songsList[0];
		};
	};
	
	$scope.remSong = function(aSong) {
		var index = $scope.songsList.indexOf(aSong);
		if (index != -1){
			$scope.songsList.splice(index, 1);
			$scope.songNumber--;
		};

	};
	
	$scope.saveList = function() {
		var name = window.prompt("Please name the list", "something");
		//console.log("data");
		//name = "zzz";
		$http.post('/playlist/', [name, $scope.songsList]).success(function(data) {
			if (data == "true") {
				$scope.getLists();
			}
		});
	};
	
	$scope.clearList = function() {
		$scope.songsList = [];
		$scope.songNumber = 0;
	};
	
	
	$scope.getLists = function() {
		$http.get('/playlist/').success(function(data) {
			//console.log(data);
			if (data != "None") {
				$scope.loadedLists = data;
				$scope.playListBool = true;
			} else {
				$scope.playListBool = false;
			}
		});
	};
	
	$scope.loadList = function(aList) {
        $http.post('/rplaylist/', aList[0]).success(function(data) {
            
            $scope.songsList = data;
            $scope.songNumber = $scope.songsList.length;
            $scope.songBeingPlayed = 0;
            $scope.changeSong();
            audio.autoplay = false
	    });	
	};
	
	$scope.dropList = function(aList) {
		var name = window.prompt("Verify the name of list to drop", "");
		if (name == aList[1]) {
			$http.delete('/playlist/?id=' + aList[0]).success(function() {
				var msg = aList[1] + " successfully dropped";
				window.alert(msg);
				$scope.getLists();
			});
		}
	}
	
	$scope.login = function() {
		if($scope.logged.show) {
			$scope.logged.show = false;
		} else {
			$scope.logged.show = true;
            $scope.error.description = ""
            $scope.error.bool = false
		}
	};
	
	$scope.logout = function() {
		$http.get('/logout/')
		$scope.logged.loggedin = false;
		$scope.logged.show = false;
		$scope.songsList = [];
		$scope.playList = [];
		$scope.songNumber = 0;
		$scope.loadedLists = [];
		$scope.songSelection = false;
		$scope.playListBool = false;
		$scope.songBeingPlayed = 0;
	};
	
	$scope.connect = function(user) {
	    $scope.error.description = ""
        $scope.error.bool = false
        if( user != undefined){
			$http({withCredentials: true, method: "post", url: "/login/", data: user}).success(function(data) {
				if(data == "False") {
					$scope.error.bool = true;
					$scope.error.description = "login error";
					user.name = "";
					user.password = "";
				}
				else {
					$scope.error.bool = true;
					$scope.logged.show = false;
					$scope.logged.loggedin = true;
					$scope.logged.name = user.name;
					user.name = "";
					user.password = "";
					$scope.getLists();
					//$location.path("/");
				}
			});
		}
	};
	
	fileInput.addEventListener("change", function() {
		var reader = new FileReader()
		var files = fileInput.files;
		if (files.length > 0) {
			for (var i = 0; i < files.length; i++) {
				reader.readAsBinaryString(files[i])
				if (i == files.length - 1) {
					reader.onloadend = (function() { 
						// console.log(reader.result);
						$http({withCredentials: true, method: "post", url: "/upload/", data: reader.result}).success(function(data) {
							$scope.getLists();
                            //console.log(fileInput.files);
                            fileInput.value = null;
                            //console.log(fileInput.files);
						});
					});
				} else {
					reader.onloadend = (function() { 
						// console.log(reader.result);
						$http({withCredentials: true, method: "post", url: "/upload/", data: reader.result})
					});
				}
			}
		}
	});
	
	audio.addEventListener('ended', function() {
		audio.autoplay = true
		$scope.$apply($scope.nextSong());
	});
	
	$scope.moveDown = function(aSong) {
		var index = $scope.songsList.indexOf(aSong);
		if (index < $scope.songNumber - 1){
			$scope.songsList.splice(index+1, 0, $scope.songsList.splice(index, 1)[0]);
		}
	};
	
	$scope.moveUp = function(aSong) {
		var index = $scope.songsList.indexOf(aSong);
		if (index > 0){
			$scope.songsList.splice(index-1, 0, $scope.songsList.splice(index, 1)[0]);
			// var downedSong = $scope.songsList.splice(index-1, 1)[0];
			// console.log($scope.songsList[index],$scope.songsList[index-1]);
			// $scope.songsList[index] = downedSong;
			// $scope.songsList[index-1] = uppedSong;
		}
	};
	
	$scope.prevSong = function() {
		if ($scope.songBeingPlayed > 0) {
			$scope.songBeingPlayed--;
			$scope.changeSong();
			audio.autoplay = true
		};
	};
	
	$scope.nextSong = function() {
		if ($scope.songBeingPlayed < $scope.songNumber - 1) {
			$scope.songBeingPlayed++;
			$scope.changeSong();
			audio.autoplay = true;
			
		} else {
			$scope.songBeingPlayed = 0
			$scope.changeSong();
			audio.autoplay = false;
			
		}
	};
	
	$scope.changeSong = function() {
		$scope.activeSong = $scope.songsList[$scope.songBeingPlayed];
	};
	
	// $scope.upLoad = function(file) {
		// console.log(file)
		// $http({withCredentials: true, method: "post", url: "/upload/", data: file}).success(function(data) {
			// $scope.getLists();
		// });
	// };
	
}

function SignInCtrl($scope, $http) {
	$scope.signinForm = new Object();
	$scope.signinForm.show = "false";
	$scope.error = new Object();
	$scope.error.bool = false;
	
	$scope.signin = function() {
		if ($scope.signinForm.show) {
			$scope.signinForm.show = false;
		} else {
			$scope.signinForm.show = true;
		}
	};
	
	$scope.sign = function(user) {
			if (user != undefined && user.name != undefined && user.password != undefined && user.password == user.passwordConf){
				var userData = new Object();
				userData.name = user.name
				userData.password = user.password
				$http({withCredentials: true, method: "post", url: "/signin/", data: userData}).success(function(data) {
					if (data == "true") {
						$scope.error.bool = false;
						$scope.signinForm.show = "false";
						var msg = user.name + " successfully registered"
						window.alert(msg)
						user.name = ""
						user.password = ""
						user.passwordConf = ""
					} else {
						$scope.error.bool = true;
						$scope.error.description = "User already exists";
						user.name = ""
						user.password = ""
						user.passwordConf = ""
					}
				});
			} else {
				console.log(user.password, user.passwordConf)
				$scope.error.bool = true;
				$scope.error.description = "Identification error";
			}
	};
}


	//$scope.play = function() {
		
	//	for (var i = 0; i < $scope.songNumber; i++) {
	//		var songPath = $scope.songsList[i][1];
			//$http.get('/Music'+songPath).success(function(aSong) {
				//$scope.playList.push(aSong);
		//	var audioElement = $document[0].createElement('audio');
			//audioElement.src = '/Music'+songPath;
			//audioElement.play();
			//aSong.play()
			//});
		//};
	//};
	
	// $scope.$watch('$document.find("audio")[0].ended', function() {
		// var ended = $document.find('audio')[0].ended
		// console.log(ended)
		// if (ended) {
			// $scope.nextSong()
		// }
	// },true);
