var socketIO = require('socket.io');
var server = require('http').createServer().listen(7000, '0.0.0.0');
var io = socketIO.listen(server,{
    extraHeaders: {
      'Content-Type' : "application/x-www-form-urlencoded"
    }
  });
var ss = require('socket.io-stream');
var path = require('path');
var fs = require('fs');
 
// Super simple server:
//  * One room only. 
//  * We expect two people max. 
//  * No error handling.

io.sockets.on('connection', function (client) {
    console.log('new connection: ' + client.id);

    client.broadcast.emit('broadcast', client.id + ' has connected');

    var stream = ss.createStream();

    fs.createReadStream('sample-video.mp4').pipe(stream);

    ss(client).emit('video-stream', stream, {
        message: 'stream file '
    });


    
    // ss(client).on('video-stream', function(stream, data) {

    // });

    // ss(client).on('profile-image', function(stream, data) {
    //     var filename = path.basename(data.name);
    //     stream.pipe(fs.createWriteStream(filename));
    //   });


    // client.on('chat', function (data) {
    //     client.broadcast.emit('chat', data);
    //     console.log(client.id + ' message: ' + JSON.stringify(data));
    // });

    
});