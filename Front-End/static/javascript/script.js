const socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    socket.send('User has connected!');
});

socket.on('message', function(msg) {
    console.log(msg);
});
