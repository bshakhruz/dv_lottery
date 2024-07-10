document.addEventListener('DOMContentLoaded', function () {
    const confirmationNumberInput = document.getElementById('txtCN');
    const confirmationNumberValidator = document.getElementById('ConfirmationNumberValidator');
    const confirmationNumberRequired = document.getElementById('ConfirmationNumberRequired');
    const txtCNValidator = document.getElementById('txtCNValidator');

    const validateConfirmationNumber = () => {
        const value = confirmationNumberInput.value;
        if (value.length !== 16) {
            confirmationNumberValidator.style.display = 'block';
            confirmationNumberRequired.style.display = 'none';
        } else {
            confirmationNumberValidator.style.display = 'none';
        }
    };

    confirmationNumberInput.addEventListener('input', validateConfirmationNumber);

    const form = document.getElementById('entrantForm');
    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(form);

        fetch('/process', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    // Update form fields with extracted data
                    document.getElementById('txtCN').value = data['Confirmation Number'] || '';
                    document.getElementById('txtLastName').value = data['Entrant Name'] || '';
                    document.getElementById('txtYOB').value = data['Year of Birth'] || '';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while processing the file.');
            });
    });
});
