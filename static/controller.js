'use strict';

//var musicshareApp = angular.module('musicshareApp', []);

/* Controllers */

baseApp.controller('SongSearchCtrl', function($scope, $http, $document, loginService) {
	$scope.songsList = [];
	$scope.playList = [];
	$scope.songNumber = 0;
	$scope.loadedLists = [];
    $scope.logged = new Object();
	$scope.logged.show = false;
	$scope.logged.name = "";
	$scope.songSelection = false;
	$scope.playListBool = false;
	$scope.songBeingPlayed = 0;
	$scope.activeSong = false;

    var baseUrl = "/musicshare/";
	
	var audio = $document.find('audio')[0]
	var fileInput = document.getElementById('fileInput')
	
	$scope.search = function(description) {
		$scope.transmit = description
		$http.post(baseUrl, description).success(function(data) {
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
		$http.post(baseUrl + 'playlist/', [name, $scope.songsList]).success(function(data) {
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
		$http.get(baseUrl + '/playlist/').success(function(data) {
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
        $http.post(baseUrl + '/rplaylist/', aList[0]).success(function(data) {
            
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
			$http.delete(baseUrl + '/playlist/?id=' + aList[0]).success(function() {
				var msg = aList[1] + " successfully dropped";
				window.alert(msg);
				$scope.getLists();
			});
		}
	}
	

	
	fileInput.addEventListener("change", function() {
		var reader = new FileReader()
		var files = fileInput.files;
		if (files.length > 0) {
			for (var i = 0; i < files.length; i++) {
				reader.readAsBinaryString(files[i])
				if (i == files.length - 1) {
					reader.onloadend = (function() { 
						// console.log(reader.result);
						$http({withCredentials: true, method: "post", url: baseUrl + "/upload/", data: reader.result}).success(function(data) {
							$scope.getLists();
                            //console.log(fileInput.files);
                            fileInput.value = null;
                            //console.log(fileInput.files);
						});
					});
				} else {
					reader.onloadend = (function() { 
						// console.log(reader.result);
						$http({withCredentials: true, method: "post", url: baseUrl + "/upload/", data: reader.result})
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

    loginService.init(baseUrl + 'login/', function(data){
        if(data != "None") {
            $scope.logged.show = true;
            $scope.logged.name = data;
            $scope.getLists();
        } else {
            $scope.logged.show = false;
        }
    });

    loginService.connectCallBack = function(){
        $scope.logged.show = true;
        $scope.getLists();
    }

    loginService.disconnectCallBack = function() {
        $scope.logged.show = false;
        $scope.loadedLists = [];
    }
	
});

