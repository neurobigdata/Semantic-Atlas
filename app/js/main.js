$(function () {
    var $words = $('#words');
    var $apply = $('#voxel-apply');
    var $voxel_x = $('#voxel-x');
    var $voxel_y = $('#voxel-y');
    var $voxel_z = $('#voxel-z');
    var $score = $('#correlation-score');
    var $slice = $('#slice');

    $apply.click(function (e) {
        e.preventDefault();

        var x = $voxel_x.val();
        var y = $voxel_y.val();
        var z = $voxel_z.val();

        if (_.isNil(x))
            x = 0;

        if (_.isNil(y))
            y = 0;

        if (_.isNil(z))
            z = 0;

        var url = 'http://localhost:9990/get_voxel_result?x=' + x + '&y=' + y + '&z=' + z + '&sub=9';

        console.log(url);

        $.get(url)
            .done(function(r) {
                $score.val(r.correlation_score);
                $slice.attr('src', 'data:image/png;base64,' + r.image_xy);
                $words.empty();
                _.each(r.most_similar, function (o) {
                    $words.append('<tr><td>' + o.similarity + '</td><td>' + o.word + '</td></tr>');
                });
            })
            .fail(function(r) {
                console.warn(r);
                if (r.status === 'error')
                    alert(r.message);
            })
            .always(function(r) {
            });
    });
});