Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJmN2RjNmYxYS01ZDNkLTRlYTctOTg2ZS1mZWQ3ZGRmMGMxNGEiLCJpZCI6MjU4NTMwLCJpYXQiOjE3MzMwOTY4NzB9.di7RA3EJEjeVQKC4zEpVTy8QiDqYmJO1E6TVAikKVQ0';
const viewer = new Cesium.Viewer("cesiumContainerEarthAtNight", {
     baseLayerPicker: false,
     animation: false,
     timeline: false, 
});

const layers = viewer.scene.imageryLayers;
const blackMarble = await Cesium.ImageryLayer.fromProviderAsync(
    Cesium.IonImageryProvider.fromAssetId(3812)
);

blackMarble.alpha = 0.5;
blackMarble.brightness = 10.0;
layers.add(blackMarble);
blackMarble.show = true;

const imageryLayers = viewer.imageryLayers;
const nightLayer = Cesium.ImageryLayer.fromProviderAsync(
    Cesium.IonImageryProvider.fromAssetId(3812),
);

const dayLayer = Cesium.ImageryLayer.fromProviderAsync(
    Cesium.IonImageryProvider.fromAssetId(2),
);
imageryLayers.add(dayLayer);
imageryLayers.lowerToBottom(dayLayer);

let dynamicLighting = true;
viewer.clock.multiplier = 5000;
function updateLighting(dynamicLighting) {
    dayLayer.show = dynamicLighting;
    viewer.scene.globe.enableLighting = dynamicLighting;
    viewer.clock.shouldAnimate = dynamicLighting;
    nightLayer.dayAlpha = dynamicLighting ? 5.0 : 10.0;
}

updateLighting(dynamicLighting); 

