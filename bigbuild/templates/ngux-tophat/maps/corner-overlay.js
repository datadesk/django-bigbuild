L.LATCornerOverlay = L.Control.extend({
    initialize: function(html, position) {
        html = typeof html !== 'undefined' ?  html : '';
        position = typeof position !== 'undefined' ?  position : 'bottomright';
        this._html = html;
        this.options.position = position;
    },
    onAdd: function(map) {
        var container = L.DomUtil.create('div', 'overlay', L.DomUtil.get('map'));
        container.innerHTML = this._html;
        return container;
    },
    update: function(html) {
        this._html = html;
        this.getContainer().innerHTML = html;
    },
    hide: function() {
        $( this.getContainer() ).css('display','none');
    },
    show: function() {
        $( this.getContainer() ).css('display','block');
    }
});
