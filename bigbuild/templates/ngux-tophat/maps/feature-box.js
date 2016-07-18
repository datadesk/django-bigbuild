L.LATFeatureBox = L.LATCornerOverlay.extend({
    onAdd: function(map) {
        var container = L.DomUtil.create('div', 'overlay featurebox', L.DomUtil.get('map'));
        container.innerHTML = this._html;
        return container;
    },
});
