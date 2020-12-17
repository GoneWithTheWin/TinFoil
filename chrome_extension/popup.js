var alarmClock = {

        onHandler : function(e) {
            chrome.alarms.create("myAlarm", {delayInMinutes: 0.5, periodInMinutes: 0.5} );
                    window.close();
        },

        offHandler : function(e) {
            chrome.alarms.clear("myAlarm");
                    window.close();
        },

        setup: function() {
            var a = document.getElementById('alarmOn');
            a.addEventListener('click',  alarmClock.onHandler );
            var a = document.getElementById('alarmOff');
            a.addEventListener('click',  alarmClock.offHandler );
        }
};

document.addEventListener('DOMContentLoaded', function () {
    alarmClock.setup();

    let reportDashboardLink = document.getElementById('reportDashboardLink');
    reportDashboardLink.addEventListener('click',  function() {
	  chrome.storage.sync.get('reportDashboardUrl', function(data) {
		  console.log("Getting reportDashboardUrl: "+data.reportDashboardUrl);
		  let reportDashboardUrl = data.reportDashboardUrl;

		  chrome.storage.sync.get('userId', function(data) {
			  console.log("Getting userId: "+data.userId);
			  userId = data.userId;
			  window.open(reportDashboardUrl+ "?used_id=" + encodeURIComponent(userId), '_blank').focus();
			});
		});
	});

});

