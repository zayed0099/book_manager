
// 🔐 Check authentication before anything else
const token = localStorage.getItem('jwtToken');
if (!token) {
    alert("You must be logged in to use this app.");
    window.location.href = routes.login;
}

document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('dataTableBody');
    const apiUrl = 'http://127.0.0.1:5000/api/v1/recovery'; // Example API endpoint

    fetch(apiUrl, {
		method: 'GET',
		headers: {
			'Authorization': `Bearer ${token}`}
		})
        .then(response => response.json())
        .then(data => {
        	console.log(data);
        	const books = data.del_books; // get the array from inside the object

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

  				// Code for Recovery option.
  				const buttonCell = document.createElement('td');
  				const recBtn = document.createElement('button');
  				recBtn.textContent = 'Recover';
          const url_recover = `http://127.0.0.1:5000/api/v1/recovery/${item.id}`;

  				// Add event listener for button click
  				recBtn.addEventListener('click', () => {
  				    alert(
  				        `Title: ${item.title} will be deleted.`
  				    );
              fetch(url_recover, {
                    method: 'PUT',
                    headers: {
                      'Authorization': `Bearer ${token}`}
                  })
                  .then(response => {
                    if (!response.ok) {
                      throw new Error('Network response was not ok ' + response.statusText);
                    }
                    // Handle successful deletion (e.g., remove from UI)
                    console.log('Resource recovered successfully');
                    alert('Book recovered successfully.');
                    location.reload();
                  })
                  .catch(error => {
                    // Handle errors (e.g., display error message)
                    console.error('There was a problem with the fetch operation:', error);
              });
  				});

  				buttonCell.appendChild(recBtn);
  				row.appendChild(buttonCell); // delete button ends

    
    // Appending all those data
              tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            tableBody.innerHTML = '<tr><td colspan="3"><i>Error loading data.</i></td></tr>';
        });
});

// All the buttons in frontend
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
