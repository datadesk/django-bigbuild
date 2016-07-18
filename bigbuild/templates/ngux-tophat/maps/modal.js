//This is a control for the big map, but can be implemented at smaller sizes as well
L.LATModalControl = L.Control.extend({
    initialize: function() {
        this.options.position = 'topleft';
    },
    onAdd: function(map) {
        var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control info-btn hidden-desktop',L.DomUtil.get('map'));
        container.innerHTML = '<a class="leaflet-bar-part leaflet-bar-part-single" href="#"><span class="lat-icon-info"></span></a>';

        $(container).click( function() {
             if ($( window ).width() > 980) {
                $("#big-box").addClass('visible-desktop').show();
                $(container).addClass('hidden-desktop');
            } else {
                $('#small-box-modal').modal('toggle');
            }
        })

        if ($( window ).width() < 980) {
            $('#small-box-modal').modal('toggle');
        }

        return container;
    },
});
