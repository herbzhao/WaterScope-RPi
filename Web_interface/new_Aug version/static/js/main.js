<script>
    "use strict";

    // control the camera parameters
    let camera_params = {
    width: 1280,
    height: 720,
    fps: 10,
    sharpness: 0,
    brightness: 50,
    contrast: 0,
    saturation: 0,
    };

    function onChangeSlider(obj){
    let param_name = $(obj).parent().prop("id");
    camera_params[param_name] = $(obj).prop('value');
    $(obj).siblings('input[type="text"]').prop('value', camera_params[param_name]);
    }

    function onChangeText(obj){
    let param_name = $(obj).parent().prop("id");
    camera_params[param_name] = $(obj).prop('value');
    $(obj).siblings('input[type="range"]').prop('value', camera_params[param_name]);
    }

    function openSetting(evt, SettingName) {
        // Declare all variables
        let i, tabcontent, tablinks;

        // Get all elements with class="tabcontent" and hide them
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }

        // Get all elements with class="tablinks" and remove the class "active"
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }

        // Show the current tab, and add an "active" class to the button that opened the tab
        document.getElementById(SettingName).style.display = "block";
        evt.currentTarget.className += " active";
    }


    // control the streaming
    const STREAM_URL = 'http://10.0.0.1:8080/?action=stream';
    const STREAM_CTL_URL = 'start_stream';
    const STREAM_STOP_URL = 'stop_stream';
    const CAPTURE_URL = 'capture';
    const MOTOR_CTL_URL = 'move';
    const LED_CTL_URL = 'led';
    const MICROSWITCH_URL = 'microswitch';

    // use ajax to update the image at STREAM_URL
    function start_stream(params){
    $.ajax({
        url: STREAM_CTL_URL,
        data: params,
        success: function(){
        load_stream(params['width'], params['height']);
        },
        error: function(){
        alert('Could not restart stream with new parameters');
        }
    });
    }

    // load stream as an image (static)
    function load_stream(width=1280, height=720){
    $('#stream_container').empty()
        .append(`<img id="stream" width="${width}" height="${height}" src="${STREAM_URL}" style=""/>`);
    }

    // stop stream
    function stop_stream(params){
    $.ajax({
        url: STREAM_STOP_URL,
        data: params,
        success: function(){
        },
        error: function(){
        }
    });
    }


    // capture image by saving the jpeg in the streaming frame
    function capture(params){
    $.ajax({
        url: CAPTURE_URL,
        data: params,
        success: function(){
        load_stream(params['width'], params['height']);
        // Simulate the user clicking on the hidden download link to prompt to save the image
        $('#capture_link')[0].click();
        },
        error: function(){
        load_stream(params['width'], params['height']);
        alert('Error when attempting to capture image');
        }
    });
    }


    // Execute this when document has loaded - start stream on loading the page
    function start_stream(){
        load_stream(camera_params['width'], camera_params['height']);
        $('.tabcontent > input[type="range"]').each(function(){
        $(this).on("change", function(){
            onChangeSlider(this);
        });
        });
        $('.tabcontent > input[type="text"]').each(function(){
        $(this).on("change", function(){
            onChangeText(this);
        });
        });
        }

        
    </script>


<!-- JQuerey scripts -->

<script>
    $(document).ready(function(){
        
/*				$("p").click(function(){
            $(this).hide();
        });*/

        // Update the value of text box with slider
        $("#brightness_slider").change(function(){
            var brightness = $("#brightness_slider").val();
            $('#brightness_text').text(brightness);
        });
        
        // Update the value of text box with slider
        $("#contrast_slider").change(function(){
            var contrast = $("#contrast_slider").val();
            $('#contrast_text').text(contrast);
        });
        

        // Update the value of text box with slider
        $("#blue_gain_slider").change(function(){
            var blue_gain = $("#blue_gain_slider").val();
            $('#blue_gain_text').text(blue_gain);
        });

        // Update the value of text box with slider
        $("#red_gain_slider").change(function(){
            var red_gain = $("#red_gain_slider").val();
            $('#red_gain_text').text(red_gain);
        });

        // Update the value of text box with slider
        $("#file_path_text").change(function(){
            var red_gain = $("#red_gain_slider").val();
            $('#red_gain_text').text(red_gain);
        });

        // run python script with a button
        $('#time_lapse_button').click(function(){
            stop_stream();
            $.ajax({
                url: '/time_lapse_module',
                //data: $('form').serialize(),
                type: 'POST',
                success: function(response) {
                    console.log(response);
                },
                error: function(error) {
                    console.log(error);
                }
            });
        });

        // run autofocus python script with a button
        $("#autofocus_button").click(function(){
            $.ajax({

                url: '/autofocus',
                type: 'POST',
                success: function(response) {
                    console.log(response);
                },
                error: function(error) {
                    console.log(error);
                },
                
            });
        });

        $('#update_parameters_button').click(function(){
            var brightness = $("#brightness_slider").val();
            var contrast = $("#contrast_slider").val();
            var blue_gain = $("#blue_gain_slider").val();
            var red_gain = $("#red_gain_slider").val();
            var filepath = $("#file_path_text").val();
            var parameters = {Brightness:brightness, Contrast:contrast, Blue_gain:blue_gain, Red_gain:red_gain, Filepath:filepath}

            $.ajax({
                url: '/update_parameters',
                type: 'POST',
                data: JSON.stringify(parameters),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                async: false,
                success: function(response, msg) {
                    console.log(response);
                    alert(msg);
                },
                error: function(error) {
                    console.log(error);
                },
            });
        });
    
        // use variables from flask directly
        $("#read_parameters_button_1").click(function(){
            $.getJSON("/read_parameters", function(result){
                alert("Data: " + result.data_2 );
            });
        });

        // use ajax or getJSON to obtain JSON file or variables from flask
        $("#read_parameters_button").click(function(){
            $.ajax({
                dataType: "json",
                url: "/read_parameters",
                success: function(result){
                    $("#brightness_slider").val(result.brightness);
                    $("#contrast_slider").val(result.contrast);
                    $("#blue_gain_slider").val(result.blue_gain);
                    $("#red_gain_slider").val(result.red_gain);
                    
                    $("#brightness_text").text(result.brightness);
                    $("#contrast_text").text(result.contrast);
                    $("#blue_gain_text").text(result.blue_gain);
                    $("#red_gain_text").text(result.red_gain);
                    $("#file_path_text").text(result.filepath);
                    
                }
            });
        });


        // Execute this when document has loaded - start stream on loading the page
        $(function(){
            load_stream(camera_params['width'], camera_params['height']);
            $('.tabcontent > input[type="range"]').each(function(){
            $(this).on("change", function(){
                onChangeSlider(this);
            });
            });
            $('.tabcontent > input[type="text"]').each(function(){
            $(this).on("change", function(){
                onChangeText(this);
            });
            });
        });

    });
</script>