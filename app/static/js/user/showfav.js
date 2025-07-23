
// 🔐 Check authentication before anything else
const token = localStorage.getItem('jwtToken');
if (!token) {
    alert("You must be logged in to use this app.");
    window.location.href = routes.login;
}

document.addEventListener('DOMContentLoaded', () => {
    const tableBody1 = document.getElementById('showfav');
    const tableBody2 = document.getElementById('showdel');
    const recoverapiUrl = 'http://127.0.0.1:5000/api/v1/recovery';
    const favapiUrl = 'http://127.0.0.1:5000/api/v1/favourites'; 

    // Get all favourite books
    fetch(favapiUrl, {
		method: 'GET',
		headers: {
			'Authorization': `Bearer ${token}`}
		})
        .then(response => response.json())
        .then(data => {
        	console.log("Full data response:", data);
        	const books = data.favourite_books; // get the array from inside the object

			    if (!Array.isArray(books)) {
			        console.error('Expected books array, got:', books);
			        tableBody1.innerHTML = '<tr><td colspan="3">No books found or error occurred.</td></tr>';
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
                // Appending all those data
                tableBody1.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            tableBody1.innerHTML = '<tr><td colspan="3"><i>Error loading data.</i></td></tr>';
        });


        // Get all dleted books
        fetch(recoverapiUrl, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`}
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const books = data.del_books; // get the array from inside the object
                console.log(books)

                if (!Array.isArray(books)) {
                    console.error('Expected books array, got:', books);
                    tableBody2.innerHTML = '<tr><td colspan="3">No books found or error occurred.</td></tr>';
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
                // Appending all those data
                tableBody2.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            tableBody2.innerHTML = '<tr><td colspan="3"><i>Error loading data.</i></td></tr>';
        });
});


// all buttons in frontend
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
