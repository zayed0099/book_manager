
// 🔐 Check authentication before anything else
const token = localStorage.getItem('jwtToken');
if (!token) {
    alert("You must be logged in to use this app.");
    window.location.href = routes.login;
}


document.getElementById('sendDataBtn').addEventListener('click', () => {

	const title = document.getElementById('titleInput').value;
	const author = document.getElementById('authorInput').value;
	const genre = document.getElementById('genreInput').value;

	const dataToSend = {
		title : title,
		author : author,
		genre : genre
	};
	
	const token = localStorage.getItem('jwtToken');

	fetch('/api/v1/books', {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${token}`,
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
			location.reload(); // This refreshes the page
		})
		.catch(error => {
			console.error('There was a problem with the fetch operation:', error);
			alert('Failed to send data.')
	});

// ✅ Clear inputs automatically after submitting
	document.getElementById('titleInput').value = "";
	document.getElementById('authorInput').value = "";
	document.getElementById('genreInput').value = "";

});

// Getting books to show in table

document.addEventListener('DOMContentLoaded', () => {
	const token = localStorage.getItem('jwtToken');
    const tableBody = document.getElementById('dataTableBody');
    const apiUrl = '/api/v1/books'; // Example API endpoint

    fetch(apiUrl, {
		method: 'GET',
		headers: {
			'Authorization': `Bearer ${token}`}
		})
        .then(response => response.json())
        .then(data => {
        	console.log(data);
        	const books = data.books; // get the array from inside the object

			    if (!Array.isArray(books)) {
			        console.error('Expected books array, got:', data);
			        tableBody.innerHTML = '<tr><td colspan="3">No books found or error occurred.</td></tr>';
			        return;
			    }

            books.forEach(item => {
                const row = document.createElement('tr');

                const titleCell = document.createElement('td');
                titleCell.textContent = item.title;
                row.appendChild(titleCell);

                const authorCell = document.createElement('td');
                authorCell.textContent = item.author;
                row.appendChild(authorCell);

                const genreCell = document.createElement('td');
                genreCell.textContent = item.genre;
                row.appendChild(genreCell);

                // Show more (Edit + Delete + Favourites)
				// ✅ Add "Show More" button cell
				const buttonCell = document.createElement('td');
				const showMoreBtn = document.createElement('button');
				showMoreBtn.textContent = 'Show More';

				// Add event listener for button click
				showMoreBtn.addEventListener('click', () => {
				    alert(
				        `Title: ${item.title}\nAuthor: ${item.author}\nGenre: ${item.genre}`
				    );
				});

				buttonCell.appendChild(showMoreBtn);
				row.appendChild(buttonCell);
                
                // Appending all those data
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            tableBody.innerHTML = '<tr><td colspan="3"><i>Error loading data.</i></td></tr>';
        });
});


// Logout Button
document.getElementById("logout").addEventListener("click", () => {
  localStorage.removeItem('jwtToken');
  window.location.href = routes.login;
});

document.getElementById("details").addEventListener("click", () => {
  window.location.href = routes.manage_books;
});

document.getElementById("recover").addEventListener("click", () => {
  window.location.href = routes.recover_deleted_books;
});

document.getElementById("favdel").addEventListener("click", () => {
  window.location.href = routes.show_favourite_and_deleted;
});

document.getElementById("admin").addEventListener("click", () => {
  window.location.href = routes.manage_admin;
});

document.getElementById("dashboard").addEventListener("click", () => {
  window.location.href = routes.dashboard;
});
