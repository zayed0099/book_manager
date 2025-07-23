// 🔐 Check authentication before anything else
const token = localStorage.getItem('jwtToken');
if (!token) {
    alert("You must be logged in to use this app.");
    window.location.href = "login.html";
}

let selectedbook = null;

document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('dataTableBody');
    const apiUrl = 'http://127.0.0.1:5000/api/v1/books'; // Example API endpoint

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

    //(Edit + Delete + Favourites)
    
          				// Code for DELETE option.
          				const buttonCell = document.createElement('td');
          				const delBtn = document.createElement('button');
          				delBtn.textContent = 'Delete';
                  const url_del = `http://127.0.0.1:5000/api/v1/books/${item.id}`;

          				// Add event listener for button click
          				delBtn.addEventListener('click', () => {
          				    alert(
          				        `Title: ${item.title} will be deleted.`
          				    );
                      fetch(url_del, {
                            method: 'DELETE',
                            headers: {
                              'Authorization': `Bearer ${token}`}
                          })
                          .then(response => {
                            if (!response.ok) {
                              throw new Error('Network response was not ok ' + response.statusText);
                            }
                            // Handle successful deletion (e.g., remove from UI)
                            console.log('Resource deleted successfully');
                            alert('Book deleted successfully.');
                            location.reload();
                          })
                          .catch(error => {
                            // Handle errors (e.g., display error message)
                            console.error('There was a problem with the fetch operation:', error);
                      });
          				});

          				buttonCell.appendChild(delBtn);
          				row.appendChild(buttonCell); // delete button ends

                  // Code for Add Favourite option.
                  const buttonCell2 = document.createElement('td');
                  const addFavBtn = document.createElement('button');
                  addFavBtn.textContent = 'Add Fav';
                  const url_add_fav = `http://127.0.0.1:5000/api/v1/favourites/${item.id}`;

                  // Add event listener for button click
                  addFavBtn.addEventListener('click', () => {
                      alert(
                          `Title: ${item.title} will be added as favourite.`
                      );
                      fetch(url_add_fav, {
                            method: 'PUT',
                            headers: {
                              'Authorization': `Bearer ${token}`}
                          })
                          .then(response => {
                            if (!response.ok) {
                              throw new Error('Network response was not ok ' + response.statusText);
                            }
                            // Handle successful deletion (e.g., remove from UI)
                            console.log('Resource added as favourite successfully');
                            alert('Book added as favourite successfully.');
                            location.reload();
                          })
                          .catch(error => {
                            // Handle errors (e.g., display error message)
                            console.error('There was a problem with the fetch operation:', error);
                      });
                  });

                  buttonCell2.appendChild(addFavBtn);
                  row.appendChild(buttonCell2); // add Favourite button ends
                

                // Code for delete from Favourite option.
                  const buttonCell3 = document.createElement('td');
                  const delFavBtn = document.createElement('button');
                  delFavBtn.textContent = 'Del Fav';
                  const url_del_fav = `http://127.0.0.1:5000/api/v1/favourites/${item.id}`;

                  // Add event listener for button click
                  delFavBtn.addEventListener('click', () => {
                      alert(
                          `Title: ${item.title} will be removed from favourite.`
                      );
                      fetch(url_del_fav, {
                            method: 'DELETE',
                            headers: {
                              'Authorization': `Bearer ${token}`}
                          })
                          .then(response => {
                            if (!response.ok) {
                              throw new Error('Network response was not ok ' + response.statusText);
                            }
                            // Handle successful deletion (e.g., remove from UI)
                            console.log('Resource removed from favourite successfully');
                            alert('Book removed from favourite successfully.');
                            location.reload();
                          })
                          .catch(error => {
                            // Handle errors (e.g., display error message)
                            console.error('There was a problem with the fetch operation:', error);
                      });
                  });

                  buttonCell3.appendChild(delFavBtn);
                  row.appendChild(buttonCell3); // delete from Favourite button ends                
              

              // Code for Updating
              // Code for Show More button (modal)
              const updateCell = document.createElement('td');
              const updateBtn = document.createElement('button');
              updateBtn.textContent = 'Update';

              updateBtn.addEventListener('click', () => {
                  selectedbook = item
                  showModal(item); // this function will open the modal and populate it
              });

              updateCell.appendChild(updateBtn);
              row.appendChild(updateCell);

    // Appending all those data
              tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            tableBody.innerHTML = '<tr><td colspan="3"><i>Error loading data.</i></td></tr>';
        });
});



// Show modal code
// Modal control logic
const modal = document.getElementById("modal");
const closeBtn = document.getElementById("closeBtn");
const modalTitle = document.getElementById("modalTitle");
const modalAuthor = document.getElementById("modalAuthor");
const modalGenre = document.getElementById("modalGenre");
const submitBtn = document.getElementById("submitChanges");

const token_ = localStorage.getItem('jwtToken');

function showModal(book) {
  modalTitle.textContent = book.title;
  modalAuthor.textContent = "Author: " + book.author;
  modalGenre.textContent = "Genre: " + book.genre;
  modal.style.display = "flex";
} // for function

closeBtn.addEventListener("click", () => {
  modal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.style.display = "none";
  }
});


submitBtn.addEventListener('click', () => {
  const titleCng = document.getElementById('modalTitlecng').value.trim();
  const authorCng = document.getElementById('modalAuthorcng').value.trim();
  const genreCng = document.getElementById('modalGenrecng').value.trim();

  let dataToSend = {};

  if (titleCng) {dataToSend.title = titleCng;}
  if (authorCng) {dataToSend.author = authorCng;}
  if (genreCng) {dataToSend.genre = genreCng;}

  if (!selectedbook) {
    alert("No book selected for update.");
    return;}

  const url_update_data = `http://127.0.0.1:5000/api/v1/books/${selectedbook.id}`;

  fetch(url_update_data, {
    method: 'PATCH', // or 'PATCH' if updating
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token_}` // if using JWT
    },
    body: JSON.stringify(dataToSend)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data);
    alert('Data updated successfully')
    selectedbook = null;
  })
  .catch(error => {
    console.error('Error:', error);
  });

}); // for submitBtn


// All the buttons in frontend
document.getElementById("dsboard").addEventListener("click", () => {
  window.location.href = "book_cr.html";
});

document.getElementById("recover").addEventListener("click", () => {
  window.location.href = "recovery.html";
});

document.getElementById("favdel").addEventListener("click", () => {
  window.location.href = "showfav.html";
});