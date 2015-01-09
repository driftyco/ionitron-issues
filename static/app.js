angular.module('app', ['ui.router', 'ngGrid'])

.config(function($stateProvider, $urlRouterProvider) {

  $urlRouterProvider.otherwise("/");

  $stateProvider

    .state('home', {
      url: "/",
      templateUrl: "partials/home.html",
      controller: 'AppCtrl',
    })

    .state('issues', {
      url: "/issues",
      templateUrl: "partials/issues.html",
      controller: 'IssueCtrl',
    });


})


.controller('AppCtrl', function($scope, $http){

    $scope.response = {'text': 'Nothing to show. Click below to manually trigger a cron task.'};

    $scope.manualCron = function(location){
      $scope.response.text = 'Making request. This might take a while...';
      $http.get('/api/' + location)
        .success(function(data){
          $scope.response.text = JSON.stringify(data);
        })
        .error(function(data){
          $scope.response.text = JSON.stringify(data);
        });
    };
})

.controller('IssueCtrl', function($scope, ScoreFactory){

    $scope.issue_data = [];
    $scope.gridOptions = {
        data: 'issue_data',
        sortInfo: { fields: ['score'], directions: ['desc']}, 
        columnDefs: [{field:'iid', displayName:'#', width:'7%',
                      cellTemplate: '<div class="ngCellText" ng-class="col.colIndex()"><a href="http://github.com/driftyco/ionic/issues/{{row.getProperty(col.field)}}">#<span ng-cell-text>{{row.getProperty(col.field)}}</span></a></div>'},
                     {field:'score', displayName:'score', width: '7%', cellFilter: 'number:0'},
                     {field: 'created_at', displayName: 'created', width: '7%'},
                     {field: 'updated_at', displayName: 'updated', width: '7%'},
                     {field:'username', displayName:'user', width: '14%', cellTemplate: '<div class="ngCellText" ng-class="col.colIndex()"><img id="thumb" ng-src="{{row.getProperty("avatar_url")}}"><a href="http://github.com/{{row.getProperty(col.field)}}"><span ng-cell-text>{{row.getProperty(col.field)}}</span></a></div>'},
                     {field: 'title', displayName: 'title', width: '58%'},
                    ]
    }

    ScoreFactory.fetchAll().then(function(data){
      console.log(data);
      // var arr = Object.keys(data).map(function (key) {return data[key]});
      $scope.issue_data = data;
    });

})

.factory('ScoreFactory', function($http, $q){

  return {

    fetchAll: function(){
      deferred = $q.defer();

      $http.get('/api/issue-scores')
        .success(function(data, status, headers, config) {
          deferred.resolve(data);
        })
        .error(function(data, status, headers, config) {
          deferred.reject(data);
        });
        return deferred.promise
    }

  }

})
