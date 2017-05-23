/**
 * Created by oliverbecher on 16/05/2017.
 */
conceptHandler = function() {

    function draw(data) {
        // some shaping
        streamgraph.draw(data);
        bars.draw(data);
    }

    function getData() {
        let params = {
            filter_id: $('input[name="filter_id"]').val(),
            bucketsize: $('input[name="bucketsize"]').val(),
            top_x: $('input[name="top_x"]').val()
        };
        $.ajax({
            url: $SCRIPT_ROOT + '/_filter',
            data: params,
            success: d => {
                handler.draw(d);
            }
    });
    }


    return {
        getData: getData,
        draw: draw
    }


}
