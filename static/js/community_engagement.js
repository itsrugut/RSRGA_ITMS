document.getElementById('feedbackForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Placeholder for form submission logic
    const name = document.getElementById('name').value;
    const message = document.getElementById('message').value;

    // Here you can add AJAX logic to send the feedback to the server

    alert('Thank you for your feedback, ' + name + '!');
    this.reset(); // Reset the form fields
});