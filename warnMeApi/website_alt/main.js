import './style.css'
var socket = io('http://localhost:3000')
let name 
fetch('http://localhost:3000/data', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text(); // or response.json() for JSON responses
        })
        .then(data => {
            console.log('Success:', data);
            document.getElementById('data').textContent = data
            name = data
        })



socket.on('message', function(msg){
    console.log(msg)
    document.getElementById('response').textContent = msg
})

