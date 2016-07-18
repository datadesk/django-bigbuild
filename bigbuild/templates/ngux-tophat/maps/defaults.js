L.Map.mergeOptions({
    zoomControl: false,
    locateControl: true,
    modalControl: true,
    maxBoundsViscosity: 1.0
});

L.Map.addInitHook(function() {
    // Add controls in the top right
    new L.Control.Zoom({ position: 'topright' }).addTo(this);

    // Add Locator if option is set
    if (this.options.locateControl === true) {
        var locateControl = new L.Control.Locate({
            drawCircle: false,
            position: 'topright',
            showPopup: false,
            icon:'lat-icon-direction',
            iconLoading: 'lat-icon-spinner animate-spin'
        });
        locateControl.addTo(this);
    }

    // Add modal, if option is set
    if (this.options.modalControl === true) {
        new L.LATModalControl().addTo(this);
    }
});
