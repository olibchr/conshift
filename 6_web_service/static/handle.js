/**
 * Created by oliverbecher on 16/05/2017.
 */
conceptHandler = function() {
    let streamgraph = coreGraph(this);
    let bars = barChart(this);

    function draw(data) {
        streamgraph.draw(data['top_core']);
        //bars.draw(data['top_adds'], '#adds');
        //bars.draw(data['top_rems'], '#rems');
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

    getData();
    document.getElementById("get_concept").onclick = function() {getData()};

    return {
        getData: getData,
        draw: draw
    }


}
