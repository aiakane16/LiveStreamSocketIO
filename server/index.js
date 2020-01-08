var express = require('express');
var app = express();
var server = require('http').Server(app);
var io = require('socket.io')(server);
var sockets = [];

app.use(express.static('public'))

server.listen(3000,function(){
    console.log('server listening on port 3000')
});

io.on('connection',function(client){
    console.log(client.id + ' connected');

    client.emit('add-users', {
        users: sockets
    });

    client.broadcast.emit('add-users', {
        users: [client.id]
    });

    client.on('make-offer',function(data){
        console.log('make-offer')
        //transform data here
        client.broadcast.emit('offer-made',{
            offer : data.offer,
            socket : client.id
        });
        
    });

    client.on('make-answer',function(data){
        console.log('make-answer')
        //transform data here
        client.broadcast.emit('answer-made',{
            socket : client.id,
            answer : data.answer
        });
    });

    client.on('disconnect', function () {
        sockets.splice(sockets.indexOf(client.id), 1);
        io.emit('remove-user', client.id);
    });
    
    sockets.push(client.id);

});




// var socketIO = require('socket.io');
// var server = require('http').createServer().listen(7000, '0.0.0.0');
// var io = socketIO.listen(server,{
//     extraHeaders: {
//       'Content-Type' : "application/x-www-form-urlencoded"
//     }
//   });
// var ss = require('socket.io-stream');
// var path = require('path');
// var fs = require('fs');
 
// // Super simple server:
// //  * One room only. 
// //  * We expect two people max. 
// //  * No error handling.

// io.sockets.on('connection', function (client) {
//     console.log('new connection: ' + client.id);

//     client.broadcast.emit('broadcast', client.id + ' has connected');

//     var stream = ss.createStream();

//     fs.createReadStream('sample-video.mp4').pipe(stream);

//     ss(client).emit('video-stream', stream, {
//         message: 'stream file '
//     });


    
//     // ss(client).on('video-stream', function(stream, data) {

//     // });

//     // ss(client).on('profile-image', function(stream, data) {
//     //     var filename = path.basename(data.name);
//     //     stream.pipe(fs.createWriteStream(filename));
//     //   });


//     // client.on('chat', function (data) {
//     //     client.broadcast.emit('chat', data);
//     //     console.log(client.id + ' message: ' + JSON.stringify(data));
//     // });

    
// });