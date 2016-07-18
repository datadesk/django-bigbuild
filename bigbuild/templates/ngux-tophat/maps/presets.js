L.LACityMap = L.Map.extend({
    homeBounds: new L.LatLngBounds(
        new L.LatLng(34, -118.8682),
        new L.LatLng(35, -117.9552)
    ),
    options: {
        minZoom: 8,
        maxZoom: 16,
        maxBounds: new L.LatLngBounds(
            new L.LatLng(33.6037, -118.8682),
            new L.LatLng(34.4368, -117.9552)
        )
    }
});
L.LACityMap.addInitHook(function() {
    this.fitBounds(this.homeBounds);
});


L.LACountyMap = L.Map.extend({
    homeBounds: new L.LatLngBounds(
        new L.LatLng(33.5, -119.1448),
        new L.LatLng(35, -117.5462)
    ),
    options: {
        minZoom: 8,
        maxZoom: 16,
        maxBounds: new L.LatLngBounds(
            new L.LatLng(32, -119.1448),
            new L.LatLng(36, -117.5462)
        )
    }
});
L.LACountyMap.addInitHook(function() {
    this.fitBounds(this.homeBounds);
});


L.SanFranciscoMap = L.Map.extend({
    homeBounds: new L.LatLngBounds(
        new L.LatLng(37.4040, -123.2137),
        new L.LatLng(38.0324, -121.9549)
    ),
    options: {
        minZoom: 9,
        maxZoom: 16,
        maxBounds: new L.LatLngBounds(
            new L.LatLng(37.4040, -123.2137),
            new L.LatLng(38.0324, -121.9549)
        )
    }
});
L.SanFranciscoMap.addInitHook(function() {
    this.fitBounds(this.homeBounds);
});

L.SoCalMap = L.Map.extend({
    homeBounds: new L.LatLngBounds(
        new L.LatLng(32.3343, -121.3473),
        new L.LatLng(35.8091, -114.1308)
    ),
    options: {
        minZoom: 6,
        maxZoom: 16,
        maxBounds: new L.LatLngBounds(
            new L.LatLng(32.3343, -121.3473),
            new L.LatLng(35.8091, -114.1308)
        )
    }
});
L.SoCalMap.addInitHook(function() {
    this.fitBounds(this.homeBounds);
});


L.CaliforniaMap = L.Map.extend({
    homeBounds: new L.LatLngBounds(
        new L.LatLng(32.2343, -124.6096),
        new L.LatLng(42.2095, -113.9308)
    ),
    options: {
        minZoom: 4,
        maxZoom: 14,
        maxBounds: new L.LatLngBounds(
            new L.LatLng(32.2343, -124.6096),
            new L.LatLng(42.2095, -113.9308)
        )
    }
});
L.CaliforniaMap.addInitHook(function() {
    this.fitBounds(this.homeBounds);
});


L.USMap = L.Map.extend({
    homeBounds: new L.LatLngBounds(
        new L.LatLng(21.5, -120),
        new L.LatLng(51.4, -25)
    ),
    options: {
        minZoom: 3,
        maxZoom: 11,
        maxBounds: new L.LatLngBounds(
            new L.LatLng(18.9117, -179.1506),
            new L.LatLng(71.4410, -25)
        )
    }
});
L.USMap.addInitHook(function() {
    this.fitBounds(this.homeBounds);
});

L.laCityMap = function (id, options) {
    return new L.LACityMap(id, options);
};

L.laCountyMap = function (id, options) {
    return new L.LACountyMap(id, options);
};

L.sanFranciscoMap = function (id, options) {
    return new L.SanFranciscoMap(id, options);
};

L.californiaMap = function (id, options) {
    return new L.CaliforniaMap(id, options);
};

L.soCalMap = function (id, options) {
    return new L.SoCalMap(id, options);
};

L.usMap = function (id, options) {
    return new L.USMap(id, options);
};
