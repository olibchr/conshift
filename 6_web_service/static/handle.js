/**
 * Created by oliverbecher on 16/05/2017.
 */
handler = function() {


}
$(function() {
    $('a#get_concept').bind('click', function() {
        $.getJSON($SCRIPT_ROOT + '/_filter', {
            filter_id: $('input[name="filter_id"]').val(),
            bucketsize: $('input[name="bucketsize"]').val(),
            top_x: $('input[name="top_x"]').val()
        }, function(data) {
            console.log(data);
            $("#result").text(data.result);
        });
        return false;
    });
});
