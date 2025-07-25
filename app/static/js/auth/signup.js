
document.getElementById('sendDataBtn').addEventListener('click', () => {

	const username = document.getElementById('usernameInput').value;
	const email = document.getElementById('emailInput').value;
	const password = document.getElementById('passInput').value;

	const dataToSend = {
		username : username,
		password : password,
		email : email 
	};
	
	fetch('http://127.0.0.1:5000/auth/v1/register', {
		method: 'POST',
		headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
	})
	.then(response => {
		if (!response.ok){
			throw new Error('Network response was not ok.');
		}
		return response.json();
	})
	.then(data => {
		console.log('Server Response:', data);
		alert('Data sent successfully');
    	window.location.href = routes.login; 
	})
	.catch(error => {
		console.error('There was a problem with the fetch operation:', error);
		alert('Failed to send data.')
	});

});

