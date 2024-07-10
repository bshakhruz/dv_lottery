document.getElementById('entrantForm').addEventListener('submit', function (e) {
    e.preventDefault();

    var formData = new FormData(this);

    fetch('/process', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                console.log(data);
                document.getElementById('txtCN').value = data['Confirmation Number'] || '';
                document.getElementById('txtLastName').value = data['Entrant Name'] || '';
                document.getElementById('txtYOB').value = data['Year of Birth'] || '';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});