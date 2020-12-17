console.log("background.js");

chrome.runtime.onInstalled.addListener(function() {
  chrome.storage.sync.set({serverUrl: 'http://ec2-13-56-191-71.us-west-1.compute.amazonaws.com:5000/hackathon/send_data'}, function() {
	  chrome.storage.sync.get('serverUrl', function(data) {
		  console.log("Set serverUrl: "+data.serverUrl);
		});
  });

  chrome.storage.sync.set({reportDashboardUrl: 'http://ec2-13-56-191-71.us-west-1.compute.amazonaws.com:5000/hackathon/show_report'}, function() {
	  chrome.storage.sync.get('reportDashboardUrl', function(data) {
		  console.log("Set reportDashboardUrl: "+data.reportDashboardUrl);
		});
  });

  let userId = new Date().getTime();
  chrome.storage.sync.set({userId: userId}, function() {
	  chrome.storage.sync.get('userId', function(data) {
		  console.log("Set userId: "+data.userId);
		});
  });

  chrome.declarativeContent.onPageChanged.removeRules(undefined, function() {
    chrome.declarativeContent.onPageChanged.addRules([{
      conditions: [new chrome.declarativeContent.PageStateMatcher({
        pageUrl: {hostEquals: 'www.facebook.com'},
      })
      ],
          actions: [new chrome.declarativeContent.ShowPageAction()]
    }]);
  });

});

chrome.alarms.onAlarm.addListener(function(alarm) {
  console.log("Timer triggered!");
  triggerCheckNewAds();
});


function triggerCheckNewAds() {
	console.log("triggerCheckNewAds");
	chrome.tabs.query({ highlighted: true}, function(tabs){
			tabs.forEach(tab => {
				console.log("sending message to tab "+tab.id+" ("+tab.url+")");
				chrome.tabs.sendMessage(tab.id, { action: "check-new-ads" });
			});
		});

};
