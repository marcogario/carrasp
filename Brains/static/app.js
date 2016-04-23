(function(io) {
    var FPS_WEIGHT = 0.1;
    socket = io.connect();

    var front_canvas = $("#camera_canvas")[0];
    var back_canvas = $("#back_camera_canvas")[0];

    front_stream = {
        startTime: new Date().getTime(),
        frameCt: 0,
        fps: $("#fps_counter")[0],
        context: front_canvas.getContext('2d'),
        canvas: front_canvas,
    };

    back_stream = {
        startTime: new Date().getTime(),
        frameCt: 0,
        fps: $("#fps_counter")[0],
        context: back_canvas.getContext('2d'),
        canvas: back_canvas,
    };


    function draw_on_canvas(stream, data, emit_key) {
        // Each time we receive an image, request a new one
        socket.emit(emit_key, data.id );

        img = new Image();
        img.src = data.raw;

        var ctx = stream.context;

        ctx.drawImage(img, 0, 0, stream.canvas.width, stream.canvas.height);

        var size = 30;
        var lw = 3;
        var cx = stream.canvas.width / 2;
        var cy = stream.canvas.height / 2;

        ctx.beginPath();
        ctx.moveTo(cx + size, cy);
        ctx.lineTo(cx - size, cy);
        ctx.lineWidth = lw;
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(cx, cy + size);
        ctx.lineTo(cx, cy - size);
        ctx.lineWidth = lw;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(cx, cy, size*2/3, 0, 2 * Math.PI, false);
        ctx.lineWidth = lw;
        ctx.stroke();

        stream.frameCt++;
    };

    socket.on('front_frame', function ( data ) {
        draw_on_canvas(front_stream, data, "front_camera");
    });

    socket.on('back_frame', function ( data ) {
        draw_on_canvas(back_stream, data, "back_camera");
    });

    socket.emit('front_camera', 0);
    socket.emit('back_camera', 0);

    // Update fps (loop)
    setInterval( function () {
        d = new Date().getTime(),
        currentTime = ( d - stream.startTime ) / 1000,
        result = Math.floor( ( stream.frameCt / currentTime ) );

        if ( currentTime > 1 ) {
            stream.startTime = new Date().getTime();
            stream.frameCt = 0;
        }

        stream.fps.innerText = result;
    }, 100 );

    // Wheels
    socket.on('wheels_data', function ( data ) {
        socket.emit('wheels', 0);
        $("#target_throttle")[0].innerText = data.target_throttle;
        $("#target_steering")[0].innerText = data.target_steering;
    });

    socket.emit('wheels', 0);

})( io );
