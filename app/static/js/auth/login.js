document.getElementById('sendDataBtn').addEventListener('click', () => {

	const username = document.getElementById('usernameInput').value;
	const password = document.getElementById('passInput').value;

	const dataToSend = {
		username : username,
		password : password
	};
	
	fetch('http://127.0.0.1:5000/auth/v1/login', {
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

				// extracting it from response and saving it in local storage
				const accessToken = data.access_token;

				if (accessToken) {
				    localStorage.setItem('jwtToken', accessToken);
				    window.location.href = routes.dashboard;
				} else {
				    alert("Login failed: No token received.");}

    			// Clearing fields
				document.getElementById('usernameInput').value = '';
				document.getElementById('passInput').value = '';
		})
			.catch(error => {
				console.error('There was a problem with the fetch operation:', error);
				alert('Login failed. Please check your credentials.');
				// alert('Failed to send data.')
	});

}); // Eventlistener ends

document.getElementById("signupBtn").addEventListener("click", () => {
  window.location.href = routes.signup;
});
