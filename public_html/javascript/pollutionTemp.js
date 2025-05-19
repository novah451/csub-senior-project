document.addEventListener('DOMContentLoaded', function () {

	Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJmN2RjNmYxYS01ZDNkLTRlYTctOTg2ZS1mZWQ3ZGRmMGMxNGEiLCJpZCI6MjU4NTMwLCJpYXQiOjE3MzMwOTY4NzB9.di7RA3EJEjeVQKC4zEpVTy8QiDqYmJO1E6TVAikKVQ0';

	const viewer = new Cesium.Viewer('cesiumContainerPollution2', {
		imageryProvider: false,
		baseLayerPicker: false,
		terrain: Cesium.Terrain.fromWorldTerrain(),
		timeline: false,
		animation: false,
		fullscreenButton: false
	});

	viewer.scene.mode = Cesium.SceneMode.SCENE2D;
	viewer.camera.setView({
		destination: Cesium.Cartesian3.fromDegrees(241.125, 35.375, 750000),
		orientation: {
			heading: 0.0,
			pitch: -90.0,
			roll: 0.0
		}
	});

	let pollutionLayers = {
		"PM2_5": [],
		"CO": [],
		"O3": [],
		"SO2": [],
		"NO": [],
		"NO2": [],
		"PM10": [],
		"all": []
	};

	let windDirectionEntities = [];
	let boardData = null;
	let pollutionData = [];
	let highestVal = {
		"PM2_5": 0, "PM2_5Low": 0.0, "PM2_5High": 0.0, "PM2_AQI_Low": 0.0, "PM2_AQI_High": 0.0,
		"CO": 0, "COLow": 0.0, "COHigh": 0.0, "CO_AQI_Low": 0.0, "CO_AQI_High": 0.0,
		"O3": 0, "O3Low": 0.0, "O3High": 0.0, "O3_AQI_Low": 0.0, "O3_AQI_High": 0.0,
		"SO2": 0, "SO2Low": 0.0, "SO2High": 0.0, "SO2_AQI_Low": 0.0, "SO2_AQI_High": 0.0,
		"NO2": 0, "NO2Low": 0.0, "NO2High": 0.0, "NO2_AQI_Low": 0.0, "NO2_AQI_High": 0.0,
		"PM10": 0, "PM10Low": 0.0, "PM10High": 0.0, "PM10_AQI_Low": 0.0, "PM10_AQI_High": 0.0,
	};

	function getColor(value, pollutant) {
		// using https://document.airnow.gov/technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf
		if (pollutant === 'PM2_5') { // µg/m³
			//if(highestVal["PM2_5"] < value)
				highestVal["PM2_5"] = value;
			// range for 6 hours
			if (value <= 9 * 0.25) {
				highestVal["PM2_5Low"] = 0.0;
				highestVal["PM2_5High"] = 9.0;
				highestVal["PM2_5_AQI_Low"] = 0;
				highestVal["PM2_5_AQI_High"] = 50;
				return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good: 0-9
			}
			if (value <= 35.4 * 0.25) {	
				highestVal["PM2_5Low"] = 9.1;
				highestVal["PM2_5High"] = 35.4;
				highestVal["PM2_5_AQI_Low"] = 51;
				highestVal["PM2_5_AQI_High"] = 100;
				return Cesium.Color.fromBytes(255, 255, 0, 192); // Moderate: 9.1-35.4 
			}
			if (value <= 55.4 * 0.25) {
				highestVal["PM2_5Low"] = 35.5;
				highestVal["PM2_5High"] = 55.4;
				highestVal["PM2_5_AQI_Low"] = 101;
				highestVal["PM2_5_AQI_High"] = 150;
				return Cesium.Color.fromBytes(255, 126, 0, 192); // Unhealthy 35.5-55.4
			}
			if (value <= 125.4 * 0.25) {
				highestVal["PM2_5Low"] = 55.5;
				highestVal["PM2_5High"] = 125.4;
				highestVal["PM2_5_AQI_Low"] = 151;
				highestVal["PM2_5_AQI_High"] = 200;
				return Cesium.Color.fromBytes(255, 0, 0, 192);  // Unhealthy: 55.5-125.4
			}
			if (value <= 225 * 0.25) { 
				highestVal["PM2_5Low"] = 125.5;
				highestVal["PM2_5High"] = 225;
				highestVal["PM2_5_AQI_Low"] = 201;
				highestVal["PM2_5_AQI_High"] = 300;
				return Cesium.Color.fromBytes(128, 0, 128, 192);// Very Unhealthy: 125.5-225
			}
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous: 225+
		}
		else if (pollutant === 'PM10') { // µg/m
			//if(highestVal["PM10"] < value)
				highestVal["PM10"] = value;
			
			// range of  6 hours
			if (value <= 54 * 0.25) {
				highestVal["PM10Low"] = 0.0;
				highestVal["PM10High"] = 54.0;
				highestVal["PM10_AQI_Low"] = 0;
				highestVal["PM10_AQI_High"] = 50;
				return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good: 0-54
			}
			if (value <= 154 * 0.25) {
				highestVal["PM10Low"] = 55.0;
				highestVal["PM10High"] = 154.0;
				highestVal["PM10_AQI_Low"] = 51;
				highestVal["PM10_AQI_High"] = 100;
				return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate: 55-154
			}
			if (value <= 254 * 0.25) {
				highestVal["PM10Low"] = 155.0;
				highestVal["PM10High"] = 254.0;
				highestVal["PM10_AQI_Low"] = 101;
				highestVal["PM10_AQI_High"] = 150;
				return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy 155-254
			}
			if (value <= 354 * 0.25) {
				highestVal["PM10Low"] = 255.0;
				highestVal["PM10High"] = 354.0;
				highestVal["PM10_AQI_Low"] = 151;
				highestVal["PM10_AQI_High"] = 200;
				return Cesium.Color.fromBytes(255, 0, 0, 192);   // Unhealthy: 255-354
			}
			if (value <= 424 * 0.25) {
				highestVal["PM10Low"] = 355.0;
				highestVal["PM10High"] = 424.0;
				highestVal["PM10_AQI_Low"] = 201;
				highestVal["PM10_AQI_High"] = 300;
				return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy: 355 - 424
			}
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous: 425+
		}
		else if (pollutant === 'CO') { // ppm
			// check conversion
			let coppm = (value * 24.45) / 28;
			//if(highestVal["CO"] < coppm)
				highestVal["CO"] = coppm;

			// range of 6 hours
			if (coppm <= 4.4 * 0.75) {
				highestVal["COLow"] = 0.0;
				highestVal["COHigh"] = 4.4;
				highestVal["CO_AQI_Low"] = 0;
				highestVal["CO_AQI_High"] = 50;
				return Cesium.Color.fromBytes(0, 255, 0, 192);    // Good: 0-4.4
			}
			if (coppm <= 9.4 * 0.75) {
				highestVal["COLow"] = 4.5;
				highestVal["COHigh"] = 9.4;
				highestVal["CO_AQI_Low"] = 51;
				highestVal["CO_AQI_High"] = 100;
				return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate: 4.5-9.4
			}
			if (coppm <= 12.4 * 0.75) {
				highestVal["COLow"] = 9.5;
				highestVal["COHigh"] = 12.4;
				highestVal["CO_AQI_Low"] = 101;
				highestVal["CO_AQI_High"] = 150;
				return Cesium.Color.fromBytes(255, 126, 0, 192); // Unhealthy  9.5-12.4
			}
			if (coppm <= 15.4 * 0.75) {
				highestVal["COLow"] = 12.5;
				highestVal["COHigh"] = 15.4;
				highestVal["CO_AQI_Low"] = 151;
				highestVal["CO_AQI_High"] = 200;
				return Cesium.Color.fromBytes(255, 0, 0, 192);   // Unhealthy: 12.5-15.4
			}
			if (coppm <= 30.4 * 0.75) {
				highestVal["COLow"] = 15.4;
				highestVal["COHigh"] = 30.4;
				highestVal["CO_AQI_Low"] = 201;
				highestVal["CO_AQI_High"] = 300;
				return Cesium.Color.fromBytes(128, 0, 128, 192); // Very Unhealthy: 15.4-30.4
			}
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous: 30.5+
		}
		else if (pollutant === 'O3') { // ppm
			let o3ppm = (value * 24.45) / 48000;
			//if(highestVal["O3"] < o3ppm)
				highestVal["O3"] = o3ppm;

			// range of 6 hours
			if (o3ppm <= 0.054 * 0.75) {
				highestVal["O3Low"] = 0.0;
				highestVal["O3High"] = 0.0054;
				highestVal["O3_AQI_Low"] = 0;
				highestVal["O3_AQI_High"] = 50;
				return Cesium.Color.fromBytes(0, 255, 0, 192);  // Good: 0-0.0054
			}
			if (o3ppm <= 0.070 * 0.75) {
				highestVal["O3Low"] = 0.0055;
				highestVal["O3High"] = 0.070;
				highestVal["O3_AQI_Low"] = 51;
				highestVal["O3_AQI_High"] = 100;
				return Cesium.Color.fromBytes(255, 255, 0, 192);   // Moderate: 0.0055-0.070
			}
			if (o3ppm <= 0.085 * 0.75) {
				highestVal["O3Low"] = 0.070;
				highestVal["O3High"] = 0.085;
				highestVal["O3_AQI_Low"] = 101;
				highestVal["O3_AQI_High"] = 150;
				return Cesium.Color.fromBytes(255, 126, 0, 192);   // Unhealthy 0.070-0.085
			}
			if (o3ppm <= 0.105 * 0.75) {
				highestVal["O3Low"] = 0.086;
				highestVal["O3High"] = 0.105;
				highestVal["O3_AQI_Low"] = 151;
				highestVal["O3_AQI_High"] = 200;
				return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy: 0.086-0.105
			}
			if (o3ppm <= 0.200 * 0.75) {
				highestVal["O3Low"] = 0.106;
				highestVal["O3High"] = 0.200;
				highestVal["O3_AQI_Low"] = 201;
				highestVal["O3_AQI_High"] = 300;
				return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy: 0.106-0.200
			}
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous: 0.200+
		}
		else if (pollutant === 'NO2') { // ppb
			let no2ppb = (value * 1000) / 46000;
			//if(highestVal["NO2"] < no2ppb)
				highestVal["NO2"] = no2ppb;

			// range of 6 hours
			if (no2ppb <= 53 * 6) {
				highestVal["NO2Low"] = 0.0;
				highestVal["NO2High"] = 53.0;
				highestVal["NO2_AQI_Low"] = 0;
				highestVal["NO2_AQI_High"] = 50;
				return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good: 0-53
			}
			if (no2ppb <= 100 * 6) {
				highestVal["NO2Low"] = 54.0;
				highestVal["NO2High"] = 100.0;
				highestVal["NO2_AQI_Low"] = 51;
				highestVal["NO2_AQI_High"] = 100;
				return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate: 54-100
			}
			if (no2ppb <= 360 * 6) {
				highestVal["NO2Low"] = 101.0;
				highestVal["NO2High"] = 360.0;
				highestVal["NO2_AQI_Low"] = 101;
				highestVal["NO2_AQI_High"] = 150;
				return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy 101-360
			}
			if (no2ppb <= 649 * 6) {
				highestVal["NO2Low"] = 361.0;
				highestVal["NO2High"] = 649.0;
				highestVal["NO2_AQI_Low"] = 151;
				highestVal["NO2_AQI_High"] = 200;
				return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy: 361-649
			}
			if (no2ppb <= 1249 * 6) {
				highestVal["NO2Low"] = 650.0;
				highestVal["NO2High"] = 1249.0;
				highestVal["NO2_AQI_Low"] = 201;
				highestVal["NO2_AQI_High"] = 300;
				return Cesium.Color.fromBytes(128, 0, 128, 192); // Very Unhealthy: 650-1249
			}
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous: 1250+
		}
		else if (pollutant === 'SO2') { // ppb
			let so2ppb = (value * 24.45 * 1000) / 64000;
			//if(highestVal["SO2"] < so2ppb)
				highestVal["SO2"] = so2ppb;
			
			// range of 6 hours
			if (so2ppb <= 35 * 6) {
				highestVal["SO2Low"] = 0.0;
				highestVal["SO2High"] = 35.0;
				highestVal["SO2_AQI_Low"] = 0;
				highestVal["SO2_AQI_High"] = 50;
				return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good: 0-35
			}
			if (so2ppb <= 75 * 6) {
				highestVal["SO2Low"] = 36.0;
				highestVal["SO2High"] = 75.0;
				highestVal["SO2_AQI_Low"] = 51;
				highestVal["SO2_AQI_High"] = 100;
				return Cesium.Color.fromBytes(255, 255, 0, 192);   // Moderate: 36-75
			}
			if (so2ppb <= 185 * 6) {
				highestVal["SO2Low"] = 76.0;
				highestVal["SO2High"] = 185.0;
				highestVal["SO2_AQI_Low"] = 101;
				highestVal["SO2_AQI_High"] = 150;
				return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy 76-185
			}
			if (so2ppb <= 304 * 6) {
				highestVal["SO2Low"] = 186.0;
				highestVal["SO2High"] = 304.0;
				highestVal["SO2_AQI_Low"] = 151;
				highestVal["SO2_AQI_High"] = 200;
				return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy: 186-304
			}
			if (so2ppb <= 604 * 6) {
				highestVal["SO2Low"] = 305.0;
				highestVal["SO2High"] = 604.0;
				highestVal["SO2_AQI_Low"] = 201;
				highestVal["SO2_AQI_High"] = 300;
				return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy: 305-604
			}
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous: 605+
		}
		else if (pollutant === 'NO') { // ppb 
			// range of 6 hours
			let noppb = (value * 24.45 * 1000) / 30000;
			if (noppb <= 50 * 6) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good: 0-50
			if (noppb <= 100 * 6) return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate: 51-100
			if (noppb <= 200 * 6) return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy 101-200
			if (noppb <= 400 * 6) return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy: 201-400
			if (noppb <= 600 * 6) return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy: 401-600
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous: 601+
		}
		return Cesium.Color.fromBytes(255, 0, 0, 128); // Default for unknown pollutant
	}

	function getAQIColor(val) {
		if (val <= 50) return Cesium.Color.fromBytes(0, 255, 0, 192);      // Good
		if (val <= 100) return Cesium.Color.fromBytes(255, 255, 0, 192);   // Moderate
		if (val <= 250) return Cesium.Color.fromBytes(255, 126, 0, 192);   // Unhealthy for Sensitive
		if (val <= 300) return Cesium.Color.fromBytes(255, 0, 0, 192);     // Unhealthy
		if (val <= 400) return Cesium.Color.fromBytes(128, 0, 128, 192);   // Very Unhealthy
		return Cesium.Color.fromBytes(128, 0, 0, 192);                     // Hazardous
	}
	function getAQI() {
		let total = [];

		// calc for PM2.5
		total[0] = ((highestVal["PM2_5_AQI_High"] - highestVal["PM2_5_AQI_Low"]) / (highestVal["PM2_5High"] - highestVal["PM2_5Low"])) *
			  	(highestVal["PM2_5"].toFixed(1) - highestVal["PM2_5Low"]) + highestVal["PM2_5_AQI_Low"];
	
		// calc for PM10
		total[1] = ((highestVal["PM10_AQI_High"] - highestVal["PM10_AQI_Low"]) / (highestVal["PM10High"] - highestVal["PM10Low"])) *
			  	(highestVal["PM10"].toFixed(0) - highestVal["PM10Low"]) + highestVal["PM10_AQI_Low"];

		// calc for CO
		total[2] = ((highestVal["CO_AQI_High"] - highestVal["CO_AQI_Low"]) / (highestVal["COHigh"] - highestVal["COLow"])) *
			  	(highestVal["CO"].toFixed(1) - highestVal["COLow"]) + highestVal["CO_AQI_Low"];

		// calc for O3
		total[3] = ((highestVal["O3_AQI_High"] - highestVal["O3_AQI_Low"]) / (highestVal["O3High"] - highestVal["O3Low"])) *
			  	(highestVal["O3"].toFixed(3) - highestVal["O3Low"]) + highestVal["O3_AQI_Low"];

		// calc for NO2
		total[4] = ((highestVal["NO2_AQI_High"] - highestVal["NO2_AQI_Low"]) / (highestVal["NO2High"] - highestVal["NO2Low"])) *
			  	(highestVal["NO2"].toFixed(0) - highestVal["NO2Low"]) + highestVal["NO2_AQI_Low"];

		// calc for SO2
		total[5] = ((highestVal["SO2_AQI_High"] - highestVal["SO2_AQI_Low"]) / (highestVal["SO2High"] - highestVal["SO2Low"])) *
			  	(highestVal["SO2"].toFixed(0) - highestVal["SO2Low"]) + highestVal["SO2_AQI_Low"];

		let max = 0;
		// return highest aqi value
		for(let i = 0; i < 6; i++) {
			console.log(total[i]);
			if(total[i] > max)
				max = total[i];
		}

		return max;
	}
	function addPollutionData(data, pollutant) {
		let total = 0;
		let count = 0;
		let color;
		let value;
		let aqiVal; 
		data.board.forEach(item => {
			const coords = [
				item.vertices[2][0], item.vertices[2][1], // Bottom-left
				item.vertices[3][0], item.vertices[3][1], // Bottom-right
				item.vertices[1][0], item.vertices[1][1], // Top-right
				item.vertices[0][0], item.vertices[0][1], // Top-left
				item.vertices[2][0], item.vertices[2][1]  // Close the loop
			];

			
			if(pollutant != "all") {
			value = item.pollution.avg[pollutant.toLowerCase()];
			if (value < 0)
				value = value * (-1);
			color = getColor(value, pollutant);
			}
			if(pollutant == "all") {
				 const pollutants = ["PM2_5", "CO", "O3", "SO2", "NO", "NO2", "PM10"];
            			 pollutants.forEach(p => {
                		 const val = Math.abs(item.pollution.avg[p.toLowerCase()] || 0);
                		 getColor(val, p); 
            			});
				value = getAQI();
				color = getAQIColor(value);
			}

			const polygon = viewer.entities.add({
				polygon: {
					hierarchy: Cesium.Cartesian3.fromDegreesArray(coords),
					material: color,
					outline: true,
					outlineColor: Cesium.Color.BLACK,
					show: true // Show the grid by default
				},
				description: `<p><b>${pollutant}:</b> ${value}</p>`
			});

			pollutionLayers[pollutant].push(polygon);
			total += value;
			count += 1;
		});
	}

	function showWindDirection(data) {
		windDirectionEntities.forEach(entity => {
			viewer.entities.remove(entity);
		});
		windDirectionEntities = [];
		data.board.forEach(item => {
			const uWind = item.u_wind_change || 0;
			const vWind = item.v_wind_change || 0;
			const windMagnitude = Math.sqrt(uWind * uWind + vWind * vWind);
			if (windMagnitude < 0.001) return;
			const centerLon = (item.vertices[0][0] + item.vertices[2][0]) / 2;
			const centerLat = (item.vertices[0][1] + item.vertices[2][1]) / 2;
			const scaleFactor = 0.1;
			const arrowLength = Math.min(Math.max(windMagnitude * scaleFactor, 0.02), 0.2);
			const normalizedU = uWind / windMagnitude;
			const normalizedV = vWind / windMagnitude;

			const endLon = centerLon + normalizedU * arrowLength;
			const endLat = centerLat + normalizedV * arrowLength;
			let arrowColor;
			if (windMagnitude > 0.1) {
				arrowColor = Cesium.Color.CYAN.withAlpha(0.8);
			} else if (windMagnitude > 0.05) {
				arrowColor = Cesium.Color.YELLOW.withAlpha(0.8);
			} else {
				arrowColor = Cesium.Color.YELLOW.withAlpha(0.8);
			}

			const arrow = viewer.entities.add({
				polyline: {
					positions: Cesium.Cartesian3.fromDegreesArray([
						centerLon, centerLat,
						endLon, endLat
					]),
					width: 2,
					material: arrowColor
				},
				description: `<p><b>Wind Direction</b><br>U: ${uWind.toFixed(4)}<br>V: ${vWind.toFixed(4)}<br>Magnitude: ${windMagnitude.toFixed(4)}</p>`
			});

			const headSize = 0.01;
			const angle = Math.atan2(normalizedV, normalizedU);
			const headAngle1 = angle + Math.PI * 3 / 4;
			const headAngle2 = angle - Math.PI * 3 / 4;

			const head1Lon = endLon + Math.cos(headAngle1) * headSize;
			const head1Lat = endLat + Math.sin(headAngle1) * headSize;

			const head2Lon = endLon + Math.cos(headAngle2) * headSize;
			const head2Lat = endLat + Math.sin(headAngle2) * headSize;

			const arrowHead = viewer.entities.add({
				polyline: {
					positions: Cesium.Cartesian3.fromDegreesArray([
						endLon, endLat,
						head1Lon, head1Lat,
						endLon, endLat,
						head2Lon, head2Lat
					]),
					width: 2,
					material: arrowColor
				}
			});

			windDirectionEntities.push(arrow);
			windDirectionEntities.push(arrowHead);
		});

		document.getElementById('windLegend').style.display = 'flex';
	}

	function hideWindDirection() {
		windDirectionEntities.forEach(entity => {
			viewer.entities.remove(entity);
		});
		windDirectionEntities = [];

		document.getElementById('windLegend').style.display = 'none';
	}



	fetch('board_2025-03-29_0600-1200.json')
		.then(response => response.json())
		.then(data => {
			boardData = data;
			const pollutants = ["PM2_5", "CO", "O3", "SO2", "NO", "NO2", "PM10", "all"];
			pollutants.forEach(pollutant => addPollutionData(data, pollutant));
			document.getElementById('clear-grid').click();
		})
		.catch(error => console.error('Error:', error));

	const windDirectionButton = document.getElementById('wind-direction');
	windDirectionButton.addEventListener('click', () => {
		if (boardData) {
			if (windDirectionEntities.length > 0) {
				hideWindDirection();
				windDirectionButton.classList.remove('active');
			} else {
				showWindDirection(boardData);
				windDirectionButton.classList.add('active');
				clearButton.classList.remove('active');
			}
		} else {
			console.error('Board data not loaded yet');
		}
	});

	const buttons = document.querySelectorAll('button[data-type]');
	buttons.forEach(button => {
		button.addEventListener('click', () => {
			const selectedType = button.getAttribute('data-type');
			if (selectedType === 'all') {
				//Object.keys(pollutionLayers).forEach(layer => {
				//	pollutionLayers[layer].forEach(polygon => {
				//		polygon.show = true;
				//	});
				//});
				// find total average for each pollutant
				addPollutionData(boardData, "all");
				


			} else {
				Object.keys(pollutionLayers).forEach(layer => {
					pollutionLayers[layer].forEach(polygon => {
						polygon.show = false;
					});
				});
				if (pollutionLayers[selectedType]) {
					pollutionLayers[selectedType].forEach(polygon => {
						polygon.show = true;
					});
				}
			}
		});
	});

	const clearButton = document.getElementById('clear-grid');
	clearButton.addEventListener('click', () => {
		Object.keys(pollutionLayers).forEach(layer => {
			pollutionLayers[layer].forEach(polygon => {
				polygon.show = false;
			});
		});
		buttons.forEach(button => button.classList.remove('active'));
	});

	let currentDate = '2024-03-04';
	let currentHour = 18;

	fetch('./json/output.json')
		.then(response => response.json())
		.then(data => {
			pollutionData = data;
			updateTimeDisplay();
		})
		.catch(error => console.error('Error loading JSON:', error));

	flatpickr("#calendar", {
		dateFormat: "Y-m-d",
		defaultDate: currentDate,
		inline: true,
		onChange: (selectedDates) => {
			currentDate = formatDate(selectedDates[0]);
			updateTimeDisplay();
		}
	});

	function formatDate(date) {
		const year = date.getFullYear();
		const month = String(date.getMonth() + 1).padStart(2, '0');
		const day = String(date.getDate()).padStart(2, '0');
		return `${year}-${month}-${day}`;
	}

	function updateTimeDisplay() {
		const formattedHour = String(currentHour).padStart(2, '0') + ':00';
		document.getElementById('current-time').innerText = formattedHour;
		updateGrid(currentDate, currentHour);
	}

	document.getElementById('decrement-time').addEventListener('click', () => {
		currentHour = (currentHour - 1 + 24) % 24;
		updateTimeDisplay();
	});

	document.getElementById('increment-time').addEventListener('click', () => {
		currentHour = (currentHour + 1) % 24;
		updateTimeDisplay();
	});

	// I couldn't update this because we don't have vertices in output.json from aqi_raw.csv
	function updateGrid(date, hour) {
		const selectedTime = `${date} ${String(hour).padStart(2, '0')}:00:00`;
		console.log(`Updating grid for: ${selectedTime}`);
		Object.keys(pollutionLayers).forEach(layer => {
			pollutionLayers[layer].forEach(polygon => {
				const dataPoint = pollutionData.find(point =>
					point.time === selectedTime &&
					parseFloat(point.lon) === parseFloat(polygon.lon) &&
					parseFloat(point.lat) === parseFloat(polygon.lat)
				);

				if (dataPoint) {
					const value = parseFloat(dataPoint[layer]);

					if (!isNaN(value)) {
						polygon.show = true;
						polygon.polygon.material = getColor(value, layer);
					} else {
						polygon.show = false;
					}
				} else {
					polygon.show = false;
				}
			});
		});
	}
	updateGrid(currentDate, currentHour);
	viewer.scene.requestRender();
});
