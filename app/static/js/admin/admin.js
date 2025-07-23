// 🔐 Check authentication before anything else
const token = localStorage.getItem('jwtToken');
if (!token) {
    alert("You must be logged in to use this app.");
    window.location.href = "login.html";
}

// console.log('connected')
let selectedadmin = null;

        // Code for table with admin
const tableBody2 = document.getElementById('userTable');
// Show all Admin Data
fetch('http://127.0.0.1:5000/a/v1/manage', {
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
  const admins = data.admins
  admins.forEach(item => {
    const row = document.createElement('tr');

    const usernamecell = document.createElement('td');
    usernamecell.textContent = item.username;
    row.appendChild(usernamecell);

    const emailcell = document.createElement('td');
    emailcell.textContent = item.email;
    row.appendChild(emailcell);

    const rolecell = document.createElement('td');
    rolecell.textContent = item.role;
    row.appendChild(rolecell);

    const updateCell = document.createElement('td');
    const updateBtn = document.createElement('button');
    updateBtn.textContent = 'Update';

    updateBtn.addEventListener('click', () => {
        selectedadmin = item
        showModal(item); // this function will open the modal and populate it
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
const modalEmail = document.getElementById("modalEmail");
const submitBtn = document.getElementById("submitChanges");

function showModal(admin) {
  modalUsername.textContent = "Username: " + admin.username;
  modalEmail.textContent = "Email: " + admin.email;
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
  const selectedRole = document.getElementById('roles').value;

  if (!selectedadmin) {
    alert("No admin selected for update.");
    return;}

  if (selectedRole === 'user') {
      const url_update_admin = `http://127.0.0.1:5000/a/v1/manage/${selectedadmin.id}`;
      fetch(url_update_admin, {
        method: 'DELETE', // or 'PATCH' if updating
        headers: {
          'Authorization': `Bearer ${token}` // if using JWT
        }
      })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
        alert(`${selectedadmin.username} removed from admin successfully`)
        selectedadmin = null;
      })
      .catch(error => {
        console.error('Error:', error);
      });
  } // if ends
  
  else if (selectedRole === 'admin') {
    const url_update_admin = `http://127.0.0.1:5000/a/v1/manage/${selectedadmin.id}`;
      fetch(url_update_admin, {
        method: 'PUT', // or 'PATCH' if updating
        headers: {
          'Authorization': `Bearer ${token}` // if using JWT
        }
      })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
        alert(`${selectedadmin.username} added as admin successfully`)
        selectedadmin = null;
      })
      .catch(error => {
        console.error('Error:', error);
      });
  } // else if ends

}); // to end the eventlistener added in submit button

      
      // Code for completely new user as new admin

document.getElementById('sendDataBtn').addEventListener('click', () => {

    const username = document.getElementById('usernameInput').value;
    const email = document.getElementById('emailInput').value;
    const password = document.getElementById('passInput').value;

    const dataToSend = {
      username : username,
      password : password,
      email : email 
    };
    
    fetch('http://127.0.0.1:5000/a/v1/manage', {
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
      alert('New Admin cretaed successfully');
      location.reload();
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
      alert('Failed to send data.')
    });

});