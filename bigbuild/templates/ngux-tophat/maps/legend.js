L.LATLegend = L.LATCornerOverlay.extend({
    onAdd: function(map) {
        var container = L.DomUtil.create('div', 'overlay legend', L.DomUtil.get('map'));
        container.innerHTML = this._html;
        return container;
    },
    addData: function(legendData) {
        var legendTemplateSwatch = _.template($('#legend-template-swatch').html());
        var legendTemplateScale = _.template($('#legend-template-scale').html());
        var defaults = {align: 'left', template: 'scale'};
        var opts = _.extend(defaults, legendData)
        if (opts.template == 'swatch') {
            var html = legendTemplateSwatch(opts);
        } else {
            var html = legendTemplateScale(opts);
        }
        this.update(html);
    },
});
