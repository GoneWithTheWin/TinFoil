let assignedIdDiv = document.getElementById('assignedUserId');
let selectedIdDiv = document.getElementById('selectedUserId');
let changeButton = document.getElementById('changeUserId');

document.addEventListener('DOMContentLoaded', function () {
    changeButton.addEventListener('click', function() {
		let selectedUserId = selectedIdDiv.value;
		console.log("selectedUserId: "+selectedUserId);

		  chrome.storage.sync.set({userId: selectedUserId}, function() {
			console.log("Set  selectedUserId: "+ selectedUserId);
		  });

		selectedIdDiv.value="";
		assignedIdDiv.innerHTML = selectedUserId;
    });

	  chrome.storage.sync.get('userId', function(data) {
		  console.log("Getting userId: "+data.userId);
		  assignedIdDiv.innerHTML = data.userId;
		});

});

