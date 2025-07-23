
// 🔐 Check authentication before anything else
const token = localStorage.getItem('jwtToken');
if (!token) {
    alert("You must be logged in to use this app.");
    window.location.href = routes.login;
}

// console.log('connected')
let selecteduser = null;

const tableBody1 = document.getElementById('allUserBooks'); 

fetch('http://127.0.0.1:5000/a/v1/books', {
method: 'GET',
headers: {
  'Authorization': `Bearer ${token}`
}
})
.then(response => {
  if (!response.ok) {
    throw new Error('Network response was not ok');
    tableBody1.innerHTML = '<tr><td colspan="3"><i>Error loading data.</i></td></tr>';
  }
  return response.json();
})

.then(data => {
  const books = data.books
  books.forEach(item => {
    const row = document.createElement('tr');

    const titleCell = document.createElement('td');
    titleCell.textContent = item.title;
    row.appendChild(titleCell);

    const authorCell = document.createElement('td');
    authorCell.textContent = item.author;
    row.appendChild(authorCell);

    const delCell = document.createElement('td');
    delCell.textContent = item.is_deleted;
    row.appendChild(delCell);

    const useridCell = document.createElement('td');
    useridCell.textContent = item.user_id;
    row.appendChild(useridCell);

    tableBody1.appendChild(row);
  });
})
.catch(error => {
  console.error('Error fetching data:', error);
  tableBody1.innerHTML = '<tr><td colspan="3"><i>Error loading data.</i></td></tr>';
});


// Code to show data of all users (username + role)

const tableBody2 = document.getElementById('allUserData'); 

fetch('http://127.0.0.1:5000/a/v1/user/view', {
method: 'GET',
headers: {
  'Authorization': `Bearer ${token}`
}
})
.then(response => {
  if (!response.ok) {
    throw new Error('Network response was not ok');
    tableBody2.innerHTML = '<tr><td colspan="3"><i>Error loading data.</i></td></tr>';
  }
  return response.json();
})

.then(data => {
  const users = data.users
  users.forEach(item => {
    const row = document.createElement('tr');

    const idCell = document.createElement('td');
    idCell.textContent = item.id;
    row.appendChild(idCell);

    const usernameCell = document.createElement('td');
    usernameCell.textContent = item.username;
    row.appendChild(usernameCell);

    const roleCell = document.createElement('td');
    roleCell.textContent = item.role;
    row.appendChild(roleCell);

    const banCell = document.createElement('td');
    banCell.textContent = item.is_banned;
    row.appendChild(banCell);

    const updateCell = document.createElement('td');
    const updateBtn = document.createElement('button');
    updateBtn.textContent = 'Manage';

    updateBtn.addEventListener('click', () => {
    	selecteduser = item
        showModal(item);
    });

    updateCell.appendChild(updateBtn);
    row.appendChild(updateCell);

    tableBody2.appendChild(row);
  });
})
.catch(error => {
  console.error('Error fetching data:', error);
  tableBody2.innerHTML = '<tr><td colspan="3"><i>Error loading data.</i></td></tr>';
});



// Show modal code
// Modal control logic
const modal = document.getElementById("modal");
const closeBtn = document.getElementById("closeBtn");
const modalUsername = document.getElementById("modalUsername");
const modalrole = document.getElementById("modalrole");
const submitBtn = document.getElementById("submitChanges");

function showModal(user) {
  modalUsername.textContent = "Username: " + user.username;
  modalrole.textContent = "Role: " + user.role;
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
  const selectedStatus = document.getElementById('status').value;

  if (!selecteduser) {
    alert("No admin selected for update.");
    return;}

  if (selectedStatus === 'ban') {
      const url_update_status = `http://127.0.0.1:5000/a/v1/user/ban/${selecteduser.id}`;
      fetch(url_update_status, {
        method: 'DELETE', // or 'PATCH' if updating
        headers: {
          'Authorization': `Bearer ${token}` // if using JWT
        }
      })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
        alert(`${selecteduser.username} has been banned from the site.`)
        selecteduser = null;
      })
      .catch(error => {
        console.error('Error:', error);
      });
  } // if ends
  
  else if (selectedStatus === 'unban') {
    const url_update_status = `http://127.0.0.1:5000/a/v1/user/ban/${selecteduser.id}`;
      fetch(url_update_status, {
        method: 'PUT', // or 'PATCH' if updating
        headers: {
          'Authorization': `Bearer ${token}` // if using JWT
        }
      })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
        alert(`${selecteduser.username} has been unbanned successfully`)
        selecteduser = null;
      })
      .catch(error => {
        console.error('Error:', error);
      });
  } // else if ends

}); // to end the eventlistener added in submit button

      
      

      // Changing users password
document.getElementById('sendDataBtn').addEventListener('click', () => {

    const username = document.getElementById('usernameInput').value;
    const email = document.getElementById('emailInput').value;
    const password = document.getElementById('passInput').value;

    const dataToSend = {
      username : username,
      password : password,
      email : email 
    };
    
    fetch('http://127.0.0.1:5000/a/v1/user/reset', {
      method: 'POST',
      headers: {
              'Content-Type': 'application/json' ,
              'Authorization': `Bearer ${token}`
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
      alert('User password changed successfully');
      location.reload();
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
      alert('Failed to send data.')
    });

});