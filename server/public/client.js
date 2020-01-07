const socket = io('http://192.168.254.102:7000');
ss.forceBase64 = true;

socket.on('connect',function(data){
    console.log('connected ')

    var mediaSource = new MediaSource();

    document.getElementById('video').src = mediaSource;

    var mimeCodec = 'video/mp4';

    mediaSource.addEventListener('sourceopen', function(event) {

        console.log(event)

        var sourceBuffer = mediaSource.addSourceBuffer(mimeCodec);

        console.log(sourceBuffer);

        ss(socket).on('video-stream', function (stream, data) {
            console.log(stream,data);
            // stream.write(new ss.Buffer([0, 1, 2]));
            // sourceBuffer.appendStream(stream)

            // socket.on('chunk', function (data) {
            //     console.log(data);
            //     sourceBuffer.append(new Uint8Array(data));
            // });
            
            stream.on('data',function(data){
                sourceBuffer.appendBuffer(data);
                console.log(data)
            })
        
            stream.on('end',function(data){
                console.log('end')
            })

        });
    });

    socket.on('broadcast', (data) => {
        console.log(data)
    });


    // ss(socket).on('video-stream',function(stream,data){
    //     console.log(data)

    //     stream.on('data',function(data){
    //         console.log(data)
    //     })
    
    //     stream.on('end',function(data){
    //         console.log(data)
    //     })
    
    //     var result = stream.pipe(stream);
    
    //     console.log(result)
    // })
})




socket.on('video-stream', (stream, data) => {
    console.log(stream, data);
   
});


// (function(){
//     var video = document.getElementById('video');
//     var vendorURL = window.URL || window.webkitURL;

//     navigator.getMedia = navigator.getUserMedia || 
//                         navigator.webkitGetUserMedia ||
//                         navigator.mozGetUserMedia ||
//                         navigator.msGetUserMedia;

//     navigator.getMedia({
//         video : true,
//         audio : false
//     },function(stream){

//         socket.emit('video-stream',stream);
        
//         video.srcObject = stream;
        
//     },function(error){
//         console.log(error)
//     });
// })();