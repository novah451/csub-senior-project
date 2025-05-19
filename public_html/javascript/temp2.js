document.addEventListener('DOMContentLoaded', function () {

	Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJmN2RjNmYxYS01ZDNkLTRlYTctOTg2ZS1mZWQ3ZGRmMGMxNGEiLCJpZCI6MjU4NTMwLCJpYXQiOjE3MzMwOTY4NzB9.di7RA3EJEjeVQKC4zEpVTy8QiDqYmJO1E6TVAikKVQ0';

	const viewer = new Cesium.Viewer('cesiumContainerPollution', {
		imageryProvider: true,
		baseLayerPicker: true,
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
		"aqi": []
	};

	let windDirectionEntities = [];
	let boardData = null;
	let pollutionData = [];

	function getColor(value, pollutant) {
		// using https://document.airnow.gov/technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf
		if (pollutant === 'PM2_5') { // µg/m�
			// range for 6 hours
			if (value <= 12) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good
			if (value <= 35.4) return Cesium.Color.fromBytes(255, 255, 0, 192); // Moderate 
			if (value <= 55.4) return Cesium.Color.fromBytes(255, 126, 0, 192); // Unhealthy 
			if (value <= 150.4) return Cesium.Color.fromBytes(255, 0, 0, 192);  // Unhealthy 
			if (value <= 250) return Cesium.Color.fromBytes(128, 0, 128, 192);// Very Unhealthy
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous 
		}
		else if (pollutant === 'PM10') { // µg/m
			// range of  6 hours
			if (value <= 54) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good: 
			if (value <= 154) return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate
			if (value <= 254) return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy 
			if (value <= 354) return Cesium.Color.fromBytes(255, 0, 0, 192);   // Unhealthy
			if (value <= 424) return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'CO') { // ppm
			// range of 6 hours
			let coppm = value / 1145;
			if (coppm <= 4.4) return Cesium.Color.fromBytes(0, 255, 0, 192);    // Good
			if (coppm <= 9.4) return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate
			if (coppm <= 12.4) return Cesium.Color.fromBytes(255, 126, 0, 192); // Unhealthy  
			if (coppm <= 15.4) return Cesium.Color.fromBytes(255, 0, 0, 192);   // Unhealthy
			if (coppm <= 30.4) return Cesium.Color.fromBytes(128, 0, 128, 192); // Very Unhealthy
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'O3') { // ppm
			// range of 6 hours
			let o3ppm = value / 1960
			if (o3ppm <= 0.054) return Cesium.Color.fromBytes(0, 255, 0, 192);  // Good
			if (o3ppm <= 0.070) return Cesium.Color.fromBytes(255, 255, 0, 192);   // Moderate
			if (o3ppm <= 0.085) return Cesium.Color.fromBytes(255, 126, 0, 192);   // Unhealthy 
			if (o3ppm <= 0.105) return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy
			if (o3ppm <= 0.200) return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'NO2') { // ppb
			// range of 6 hours
			let no2ppb = value / 1.88;
			if (no2ppb <= 53) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good
			if (no2ppb <= 100) return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate
			if (no2ppb <= 360) return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy
			if (no2ppb <= 649) return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy
			if (no2ppb <= 1249) return Cesium.Color.fromBytes(128, 0, 128, 192); // Very Unhealthy
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'SO2') { // ppb
			// range of 6 hours
			let so2ppb = value / 2.62;
			if (so2ppb <= 35) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good
			if (so2ppb <= 75) return Cesium.Color.fromBytes(255, 255, 0, 192);   // Moderate
			if (so2ppb <= 185) return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy 
			if (so2ppb <= 304) return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy
			if (so2ppb <= 604) return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'NO') { // ppb 
			if (value <= 50 * 6) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good
			if (value <= 100 * 6) return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate
			if (value <= 200 * 6) return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy
			if (value <= 400 * 6) return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy
			if (value <= 600 * 6) return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy
			return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'aqi') {
	                if (value <= 2) return Cesium.Color.fromBytes(0, 255, 0, 192);      // Good
                	if (value <= 3) return Cesium.Color.fromBytes(255, 255, 0, 192);   // Moderate
                	if (value <= 4) return Cesium.Color.fromBytes(255, 126, 0, 192);   // Unhealthy for Sensitive
                	if (value <= 5) return Cesium.Color.fromBytes(255, 0, 0, 192);     // Unhealthy
                	return Cesium.Color.fromBytes(128, 0, 0, 192);                     // Hazardous
		}
		return Cesium.Color.fromBytes(255, 0, 0, 128); // Default for unknown pollutant
	}

	function addPollutionData(data, pollutant) {
		let total = 0;
		let count = 0;
		let color;
		let value;
		data.board.forEach(item => {
			const coords = [
				item.vertices[2][0], item.vertices[2][1], // Bottom-left
				item.vertices[3][0], item.vertices[3][1], // Bottom-right
				item.vertices[1][0], item.vertices[1][1], // Top-right
				item.vertices[0][0], item.vertices[0][1], // Top-left
				item.vertices[2][0], item.vertices[2][1]  // Close the loop
			];

			
			value = item.pollution.avg[pollutant.toLowerCase()];
			if (value < 0)
				value = value * (-1);
			color = getColor(value, pollutant);

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



	fetch('aqiboard.json')
		.then(response => response.json())
		.then(data => {
			boardData = data;
			const pollutants = ["PM2_5", "CO", "O3", "SO2", "NO", "NO2", "PM10", "aqi"];
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
			//if (selectedType === 'all') {
			//	Object.keys(pollutionLayers).forEach(layer => {
			//		pollutionLayers[layer].forEach(polygon => {
			//			polygon.show = true;
			//		});
			//	});
				


			//} else {
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
			//}
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
