document.addEventListener('DOMContentLoaded', function () {

	Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJmN2RjNmYxYS01ZDNkLTRlYTctOTg2ZS1mZWQ3ZGRmMGMxNGEiLCJpZCI6MjU4NTMwLCJpYXQiOjE3MzMwOTY4NzB9.di7RA3EJEjeVQKC4zEpVTy8QiDqYmJO1E6TVAikKVQ0';


	const viewer = new Cesium.Viewer('cesiumContainerPollution', {
		// comment the first 2 lines and uncomment the next 2 lines to get map names
		//imageryProvider: false,
		//baseLayerPicker: false,
		baseLayer: Cesium.ImageryLayer.fromWorldImagery({
			style: Cesium.IonWorldImageryStyle.AERIAL_WITH_LABELS,
		}),
		terrain: Cesium.Terrain.fromWorldTerrain(),
		timeline: false,
		animation: false,
		fullscreenButton: false,
	});

	viewer.scene.mode = Cesium.SceneMode.SCENE2D;
	viewer.camera.setView({
		destination: Cesium.Cartesian3.fromDegrees(241.125, 35.375, 850000),
		orientation: {
			heading: 0.0,
			pitch: -90.0,
			roll: 0.0
		}
	});

	let pollutionLayers = {
		"aqi": [],
		"PM2_5": [],
		"CO": [],
		"O3": [],
		"SO2": [],
		"NO": [],
		"NO2": [],
		"PM10": []
	};

	let windDirectionEntities = [];
	let boardData = {};
	let pollutionData = [];
	let currentPollutant = "aqi";
	let currentTime = "00:00";
	let buttonOn = false;

	function getColor(value, pollutant) {
		if (pollutant === 'PM2_5') {
			//CORRECT RANGES BELOW
			// range for 6 hours
                        if (value <= 12) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good
                        if (value <= 35.4) return Cesium.Color.fromBytes(255, 255, 0, 192); // Moderate
                        if (value <= 55.4) return Cesium.Color.fromBytes(255, 126, 0, 192); // Unhealthy
                        if (value <= 150.4) return Cesium.Color.fromBytes(255, 0, 0, 192);  // Unhealthy
                        if (value <= 250) return Cesium.Color.fromBytes(128, 0, 128, 192);// Very Unhealthy
                        return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'CO') {
			//CORRECT RANGES BELOW
 			// range of 6 hours
                        let coppm = value / 1145;
                        if (coppm <= 4.4) return Cesium.Color.fromBytes(0, 255, 0, 192);    // Good
                        if (coppm <= 9.4) return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate
                        if (coppm <= 12.4) return Cesium.Color.fromBytes(255, 126, 0, 192); // Unhealthy
                        if (coppm <= 15.4) return Cesium.Color.fromBytes(255, 0, 0, 192);   // Unhealthy
                        if (coppm <= 30.4) return Cesium.Color.fromBytes(128, 0, 128, 192); // Very Unhealthy
                        return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'O3') {
			// CORRECT RANGES BELOW
			// range of 6 hours
                        let o3ppm = value / 1960
                        if (o3ppm <= 0.054) return Cesium.Color.fromBytes(0, 255, 0, 192);  // Good
                        if (o3ppm <= 0.070) return Cesium.Color.fromBytes(255, 255, 0, 192);   // Moderate
                        if (o3ppm <= 0.085) return Cesium.Color.fromBytes(255, 126, 0, 192);   // Unhealthy
                        if (o3ppm <= 0.105) return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy
                        if (o3ppm <= 0.200) return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy
                        return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'SO2') {
			// CORRECT RANGES BELOW
			// range of 6 hours
                        let so2ppb = value / 2.62;
                        if (so2ppb <= 35) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good
                        if (so2ppb <= 75) return Cesium.Color.fromBytes(255, 255, 0, 192);   // Moderate
                        if (so2ppb <= 185) return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy
                        if (so2ppb <= 304) return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy
                        if (so2ppb <= 604) return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy
                        return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'NO') {
			//CORRECT RANGES BELOW
			 if (value <= 50 * 6) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good
                        if (value <= 100 * 6) return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate
                        if (value <= 200 * 6) return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy
                        if (value <= 400 * 6) return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy
                        if (value <= 600 * 6) return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy
                        return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'NO2') {
			//CORRECT RANGES BELOW
			 // range of 6 hours
                        let no2ppb = value / 1.88;
                        if (no2ppb <= 53) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good
                        if (no2ppb <= 100) return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate
                        if (no2ppb <= 360) return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy
                        if (no2ppb <= 649) return Cesium.Color.fromBytes(255, 0, 0, 192);    // Unhealthy
                        if (no2ppb <= 1249) return Cesium.Color.fromBytes(128, 0, 128, 192); // Very Unhealthy
                        return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'PM10') {
			//CORRECT RANGES BELOW
			// range of  6 hours
                        if (value <= 54) return Cesium.Color.fromBytes(0, 255, 0, 192);     // Good:
                        if (value <= 154) return Cesium.Color.fromBytes(255, 255, 0, 192);  // Moderate
                        if (value <= 254) return Cesium.Color.fromBytes(255, 126, 0, 192);  // Unhealthy
                        if (value <= 354) return Cesium.Color.fromBytes(255, 0, 0, 192);   // Unhealthy
                        if (value <= 424) return Cesium.Color.fromBytes(128, 0, 128, 192);  // Very Unhealthy
                        return Cesium.Color.fromBytes(128, 0, 0, 192);                      // Hazardous
		}
		else if (pollutant === 'aqi') {
			if (value <= 2.5) return Cesium.Color.fromBytes(0, 255, 0, 192);      // Good
                        if (value <= 3) return Cesium.Color.fromBytes(255, 255, 0, 192);   // Moderate
                        if (value <= 4) return Cesium.Color.fromBytes(255, 126, 0, 192);   // Unhealthy for Sensitive
                        if (value <= 5) return Cesium.Color.fromBytes(255, 0, 0, 192);     // Unhealthy
                        return Cesium.Color.fromBytes(128, 0, 0, 192);                     // Hazardous
		}
	}

	function clearAllLayers() {
		// Clear all pollution layers
		Object.keys(pollutionLayers).forEach(pollutant => {
			pollutionLayers[pollutant].forEach(entity => {
				viewer.entities.remove(entity);
			});
			pollutionLayers[pollutant] = [];
		});

		// Clear wind direction entities
		hideWindDirection();
	}

	function addPollutionData(data, pollutant) {
		if (!data || !data.board) {
			console.error('Invalid data for pollutant:', pollutant);
			return;
		}

		let total = 0;
		let count = 0;

		data.board.forEach(item => {
			const coords = [ 
				item.vertices[2][0], item.vertices[2][1], // Bottom-left
				item.vertices[3][0], item.vertices[3][1], // Bottom-right
				item.vertices[1][0], item.vertices[1][1], // Top-right
				item.vertices[0][0], item.vertices[0][1], // Top-left
				item.vertices[2][0], item.vertices[2][1]  // Close the loop
			];
			
			let value = item.pollution.avg[pollutant.toLowerCase()] || 0; 
			if (value < 0)
				value = value * (-1);
			const color = getColor(value, pollutant);

			const polygon = viewer.entities.add({
				name: "Kern County" + " " + `${pollutant}`,
				polygon: {
					hierarchy: Cesium.Cartesian3.fromDegreesArray(coords),
					material: color,
					outline: false,
					outlineColor: Cesium.Color.BLACK,
					show: pollutant === currentPollutant // Only show if it's the current pollutant
				},
				properties: { 
					center: item.center
				},
				description: `<p><b>${pollutant}:</b> ${value}</p>
					      <p><b>Center:</b> ${item.center}</p>`

			});

			const polyline = viewer.entities.add({
				polyline: {
        				positions: Cesium.Cartesian3.fromDegreesArray(coords),
        				width: 1.0, 
        				material: Cesium.Color.BLACK
    				}
			});


			pollutionLayers[pollutant].push(polygon);
			total += value;
			count += 1;
		});

	}

	function showWindDirection(data) {
		if (!data || !data.board) {
			console.error('Invalid data for wind direction');
			return;
		}
	
		hideWindDirection(); // Clear existing wind direction entities
	
		data.board.forEach(item => {
			// FIX: Access the wind data from the weather object
			const uWind = item.weather?.u_wind_change || 0;
			const vWind = item.weather?.v_wind_change || 0;
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
	}
	function hideWindDirection() {
		windDirectionEntities.forEach(entity => {
			viewer.entities.remove(entity);
		});
		windDirectionEntities = [];
	}

	function getFileNameForTime(time) {
		const date = "2025-05-01";
		switch(time) {
			case "00:00":
				return `board_archive2/board_${date}_0000-0600.json`;
			case "06:00":
				return `board_archive2/board_${date}_0600-1200.json`;
			case "12:00":
				return `board_archive2/board_${date}_1200-1800.json`;
			case "18:00":
				return `board_archive2/board_${date}_1800-0000.json`;
			default:
				return `board_archive2/board_${date}_0000-0600.json`;
		}
	}

	function loadDataForTime(time) {
		const fileName = getFileNameForTime(time);

		if (boardData[time]) {
			updateDisplay(time);
			return;
		}

		fetch(fileName)
			.then(response => response.json())
			.then(data => {
				boardData[time] = data;
				updateDisplay(time);
				if(buttonOn)
					displayOrigin();
			})
			.catch(error => console.error(`Error loading data for ${time}:`, error));
	}

	function updateDisplay(time) {
		currentTime = time;
		
		console.log(currentDate);
		if(currentDate == "2025-05-02")  
			document.getElementById("gridTitle").innerHTML = "Kern County Pollution Path: " + currentDate + " at " + currentTime + " [FORECAST]";
		else
			document.getElementById("gridTitle").innerHTML = "Kern County Pollution Path: " + currentDate + " at " + currentTime + " [LIVE]";

		clearAllLayers();

		const data = boardData[time];

		if (!data) {
			console.error(`No data available for time: ${time}`);
			return;
		}

		const pollutants = ["aqi", "PM2_5", "CO", "O3", "SO2", "NO", "NO2", "PM10"];
		pollutants.forEach(pollutant => {
			addPollutionData(data, pollutant);
		});

		updatePollutantDisplay(currentPollutant);

		const windDirectionButton = document.getElementById('wind-direction');
		if (windDirectionButton.classList.contains('active')) {
			showWindDirection(data);
		}

		if(buttonOn)
			displayOrigin();
	}

	function updatePollutantDisplay(pollutant) {
		currentPollutant = pollutant;

		Object.keys(pollutionLayers).forEach(p => {
			pollutionLayers[p].forEach(entity => {
				entity.polygon.show = false;
			});
		});

		if (pollutionLayers[pollutant]) {
			pollutionLayers[pollutant].forEach(entity => {
				entity.polygon.show = true;
			});
		}
	}

	const pollutantButtons = document.querySelectorAll('.pollutant-btn');
	pollutantButtons.forEach(button => {
		button.addEventListener('click', () => {
			pollutantButtons.forEach(btn => btn.classList.remove('active'));

			button.classList.add('active');

			updatePollutantDisplay(button.getAttribute('data-pollutant'));

			if(buttonOn)
				displayOrigin();
		});
	});

	const windDirectionButton = document.getElementById('wind-direction');
	windDirectionButton.addEventListener('click', () => {
		if (boardData[currentTime]) {
			if (windDirectionButton.classList.contains('active')) {
				hideWindDirection();
				windDirectionButton.classList.remove('active');
			} else {
				showWindDirection(boardData[currentTime]);
				windDirectionButton.classList.add('active');
			}
		} else {
			console.error('Board data not loaded yet for current time');
		}
	});


	const clearButton = document.getElementById('clear-grid');
	clearButton.addEventListener('click', () => {
		clearAllLayers();
		pollutantButtons.forEach(btn => {
			if (btn.getAttribute('data-pollutant') === 'aqi') {
				btn.classList.add('active');
			} else {
				btn.classList.remove('active');
			}
		});

		timeButtons.forEach(btn => {
			if (btn.getAttribute('data-time') === '12:00') {
				btn.classList.add('active');
			} else {
				btn.classList.remove('active');
			}
		});

		windDirectionButton.classList.remove('active');

		currentPollutant = 'aqi';
		currentTime = '12:00';
		loadDataForTime('12:00');
	});

	loadDataForTime('12:00');


	let currentDate = '2025-05-01';
	let currentHour = 12;
	let calendarDateSelected = false;
	let dat = 0;
	//javascript date parsing
	function formatDate(date) {
		const year = date.getFullYear();
		const month = String(date.getMonth()+1).padStart(2, '0');
		const day = String(date.getDate()).padStart(2, '0');
		return `${year}-${month}-${day}`;
	}
	function loadDataForDateAndTime(date, time) {
		let fileName = `board_archive2/board_${date}_`;
		switch(time) {
			case "00:00": fileName += "0000-0600.json";
				break;
			case "06:00": fileName += "0600-1200.json"; 
				break;
			case "12:00": fileName += "1200-1800.json"; 
				break;
			case "18:00": fileName += "1800-0000.json"; 
				break;
			default: fileName += "0000-0600.json";
		}
		fetch(fileName)
			.then(response => response.json())
			.then(data => {
				boardData[time] = data;
				currentTime = time;
				updateDisplay(time);
				document.querySelectorAll('.time-btn').forEach(btn => {
					if (btn.getAttribute('data-time') === time) {
						btn.classList.add('active');
					} else {
						btn.classList.remove('active');
					}
				});
			})
			.catch(error => {
				console.error(`Error with ${fileName}:`, error);
			});
	}
	//same as before but now loadDataForDateAndTime
	
	flatpickr("#calendar", {
		dateFormat: "Y-m-d",
		defaultDate: currentDate,
		inline: true,
		onChange: (selectedDates) => {
			currentDate = formatDate(selectedDates[0]);
			calendarDateSelected = true;
			loadDataForDateAndTime(currentDate, "00:00");
		}
	});
	//added an if else button based on the day. if its the current day program works as before if 
	//if its a different day the program changes the data displayed on the map
	const timeButtons = document.querySelectorAll('.time-btn');
	timeButtons.forEach(button => {
		button.addEventListener('click', () => {
			timeButtons.forEach(btn => btn.classList.remove('active'));
			button.classList.add('active');
			if (calendarDateSelected) {
				loadDataForDateAndTime(currentDate, button.getAttribute('data-time'));
			} else {
				loadDataForTime(button.getAttribute('data-time'));
			}
		});
	});

	// display origin and path for the selected time
	const originButton = document.getElementById('origin-path');
	originButton.addEventListener('click', () => {
		buttonOn = !buttonOn;

		//if(buttonOn)
			displayOrigin();
	});


	function displayOrigin() {
		let csvFile = `eval/${currentDate}_evaluation_`;
		switch(currentTime) {
			case "00:00": csvFile += "0000-0600.csv";
				break;
			case "06:00": csvFile += "0600-1200.csv";
				break;
			case "12:00": csvFile += "1200-1800.csv";
				break;
			case "18:00": csvFile += "1800-0000.csv";
				break;
			default: csvFile += "0000-0600.csv";
		}
		let csvData = [];
		let origin = [];
		let path = [];
		let op = 230;
		// get the csv file that contains origin and path
		fetch(csvFile)
			.then(response => response.text())
			.then(data => {
				const rows = data.split('\n'); 
				console.log(rows); 
				for (let i = 0; i < rows.length; i++) {
					csvData[i] = rows[i].split(",");
				}
				// save origin center point here
				origin[0] = csvData[1][0];
				origin[1] = csvData[1][1];

				// save the path towards origin (center points)
				path[0] = csvData[2][0];
				path[1] = csvData[2][1];

				path[2] = csvData[3][0];
				path[3] = csvData[3][1];

				path[4] = csvData[4][0];
				path[5] = csvData[4][1];

				path[6] = csvData[5][0];
				path[7] = csvData[5][1];

				

				// loop through the squares and check for origin and path
				viewer.entities.values.forEach(function(polygon) {
					if(polygon.polygon) {
					const center = polygon.properties.center.getValue(Cesium.JulianDate.now());
					if(center[0] == parseFloat(origin[0]) && center[1] == parseFloat(origin[1])) {
						console.log("center true");
						// whatever we want to determine the center to look like here
						polygon.polygon.material = Cesium.Color.fromBytes(0, 0, 139, 255); // blue

					}
					for(let i = 0; i < 8; i = i + 2) {
						if(center[0] == parseFloat(path[i]) && center[1] == parseFloat(path[i + 1])) {
							console.log("path true");
							// again same as center 
							polygon.polygon.material = Cesium.Color.fromBytes(105, 105, 105, op); // 
							op = op - 30;
						 	
						}
					}
					}
				});
				
			});
	}
});
