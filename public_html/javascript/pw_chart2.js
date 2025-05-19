function loadData(file) {
    d3.json(file).then(data => {
        createCombinedChart(data);
    }).catch(error => {
        console.error('Error loading the JSON file:', error);
    });
}

function addLegend(svg, width, margin) {
    const windChangeColors = {
        "u_wind_change": "#00acc1",  // Deeper cyan
        "v_wind_change": "#0097a7"   // Darker cyan
    };

    const pollutionColors = {
        "co": "#FFA500",
        "no": "#FF8C00",
        "no2": "#FF6347",
        "o3": "#FF4500",
        "so2": "#FF0000",
        "pm2_5": "#B22222",
        "pm10": "#8B0000",
        "aqi": "#800080"  // Added AQI
    };
//went down to only u and v changes
    const windChangeFullNames = {
        "u_wind_change": "U Wind Changes",
        "v_wind_change": "V Wind Changes"
    };

    const pollutionFullNames = {
        'pm2_5': 'Particulate Matter at 2.5',
        'co': 'Carbon Monoxide (CO)',
        'o3': 'Harmful Ozone Gas (O3)',
        'so2': 'Sulfur Dioxide (SO2)',
        'no': 'Nitric Oxide (NO)',
        'no2': 'Nitrogen Dioxide (NO2)',
        'pm10': 'Particulate Matter at 10',
        'aqi': 'Air Quality Index (AQI)'
    };

    const windLegend = svg.append('g').attr('transform', `translate(${width + 50}, ${margin.top + 50})`);
    Object.keys(windChangeColors).forEach((key, i) => {
        windLegend.append('rect')
            .attr('x', 0)
            .attr('y', i * 20)
            .attr('width', 12)
            .attr('height', 12)
            .attr('fill', windChangeColors[key]);

        windLegend.append('text')
            .attr('x', 18)
            .attr('y', i * 20 + 10)
            .attr('font-size', '10px')
            .attr('fill', 'white') 
            .text(windChangeFullNames[key]);
    });

    const pollutionLegend = svg.append('g').attr('transform', `translate(${width + 50}, ${margin.top + 150})`);
    Object.keys(pollutionColors).forEach((key, i) => {
        pollutionLegend.append('rect')
            .attr('x', 0)
            .attr('y', i * 20)
            .attr('width', 12)
            .attr('height', 12)
            .attr('fill', pollutionColors[key]);

        pollutionLegend.append('text')
            .attr('x', 18)
            .attr('y', i * 20 + 10)
            .attr('font-size', '10px')
            .attr('fill', 'white') 
            .text(pollutionFullNames[key]);
    });
}

function createCombinedChart(data) {
    const width = 900;
    const height = 450;
    const margin = { top: 60, right: 1, bottom: 100, left: 50 };

    const svg = d3.select('#svgId').attr('width', width).attr('height', height);
    svg.selectAll('*').remove();

    addLegend(svg, width, margin);
    
    //time display as a title on the chart
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', margin.top / 2)
        .attr('text-anchor', 'middle')
        .attr('font-size', '18px')
        .attr('font-weight', 'bold')
        .attr('fill', 'white')
        .text(`Current Time: ${timeSteps[currentIndex].label}`);

    // Extract data for plotting - transform the data structure from your JSON
    // Check the structure of the data first
    console.log("Data structure:", data);
    
    // Adapt to the structure from your first file
    let plotData;
    if (data.board && Array.isArray(data.board)) {
        plotData = data.board.map(cell => {
            const pollutionData = {
                center: cell.center ? cell.center.join(',') : 'Unknown',
                u_wind_change: cell.weather ? cell.weather.u_wind_change : 0,
                v_wind_change: cell.weather ? cell.weather.v_wind_change : 0
            };
            
            // Add pollution values from the avg field if available
            if (cell.pollution && cell.pollution.avg) {
                Object.keys(cell.pollution.avg).forEach(key => {
                    pollutionData[key] = cell.pollution.avg[key];
                });
            }
            
            return pollutionData;
        });
    } else {
        // Fallback to handle the structure in the second file
        plotData = data.board || [];
    }
    

    const windChangeColors = {
        "u_wind_change": "#0077ff",  // Vivid blue
        "v_wind_change": "#002b80"   // Dark navy blue
    };

    const pollutionColors = {
        "co": "#FFA500", 
        "no": "#FF8C00", 
        "no2": "#FF6347", 
        "o3": "#FF4500", 
        "so2": "#FF0000", 
        "pm2_5": "#B22222", 
        "pm10": "#8B0000"
    };

    const xScale = d3.scaleLinear().domain([0, plotData.length - 1]).range([margin.left, width - margin.right]);
    const p_XScale = xScale;
//
    // Find min and max for wind change values to set the scale
    const windChangeMin = d3.min(plotData, d => Math.min(d.u_wind_change || 0, d.v_wind_change || 0));
    const windChangeMax = d3.max(plotData, d => Math.max(d.u_wind_change || 0, d.v_wind_change || 0));
    
    const windChangeYScale = d3.scaleLinear()
        .domain([windChangeMin, windChangeMax])
        .range([height / 2 - 20, margin.top + 20]);
//
    // Find max for pollution values for the scale
    const pollutionMax = d3.max(plotData, d => 
        Math.max(
            d.co || 0, 
            d.no || 0, 
            d.no2 || 0, 
            d.o3 || 0, 
            d.so2 || 0, 
            d.pm2_5 || 0, 
            d.pm10 || 0
        )
    );
//
    const pollutionYScale = d3.scaleLinear()
        .domain([0, pollutionMax])
        .range([height - margin.bottom, height / 2 + 20]);
//
    const tooltip = d3.select('body').append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0)
        .style('position', 'absolute')
        .style('background-color', 'rgba(0, 0, 0, 0.9)')
        .style('color', '#e0e0e0')
        .style('padding', '10px')
        .style('border-radius', '5px')
        .style('pointer-events', 'none')
        .style('z-index', '100')
        .style('font-size', '12px');

    // Draw wind change lines
    Object.keys(windChangeColors).forEach(key => {
        svg.append('path')
            .datum(plotData)
            .attr('fill', windChangeColors[key])
            .attr('opacity', 0.25)
            .attr('d', d3.area()
                .x((d, i) => xScale(i))
                .y0(windChangeYScale(0))
                .y1(d => windChangeYScale(d[key] || 0))
                .curve(d3.curveCatmullRom));

        const line = svg.append('path')
            .datum(plotData)
            .attr('stroke', windChangeColors[key])
            .attr('stroke-width', 1.5)
            .attr('fill', 'none')
            .attr('d', d3.line()
                .x((d, i) => xScale(i))
                .y(d => windChangeYScale(d[key] || 0))
                .curve(d3.curveCatmullRom));

        const len = line.node().getTotalLength();
        line.attr('stroke-dasharray', `${len} ${len}`)
            .attr('stroke-dashoffset', len)
            .transition()
            .duration(4000)
            .attr('stroke-dashoffset', 0);
    });

    Object.keys(pollutionColors).forEach((key) => {
        const barWidth = (width - margin.left - margin.right) / plotData.length;
        svg.selectAll(`.pollution_${key}`)
            .data(plotData)
            .enter()
            .append('rect')
            .attr('x', (d, i) => p_XScale(i))
            .attr('y', d => pollutionYScale(d[key] || 0))
            .attr('width', barWidth - 1)
            .attr('height', d => Math.max(0, height - margin.bottom - pollutionYScale(d[key] || 0)))
            .attr('fill', pollutionColors[key])
            .on('mouseover', (event, d) => {
                tooltip.style('opacity', 1)
                    .html(`${key.toUpperCase()}: ${(d[key] || 0).toFixed(4)}`)
                    .style('left', `${event.pageX + 8}px`)
                    .style('top', `${event.pageY - 30}px`);
                d3.select(event.target).attr('opacity', 0.7);
            })
            .on('mouseout', () => {
                tooltip.style('opacity', 0);
                d3.selectAll('rect').attr('opacity', 1);
            });
    });

    svg.append('g')
        .attr('transform', `translate(0, ${height / 2 - 20})`)
        .call(d3.axisBottom(xScale).tickFormat(i => plotData[i].center))
        .selectAll('text')
        .style('font-size', '10px')
        .attr('dx', '-0.5em')
        .attr('dy', '0.25em');

    svg.append('g')
        .attr('transform', `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(p_XScale).tickFormat(i => plotData[i].center))
        .selectAll('text')
        .style('font-size', '10px')
        .attr('dx', '-0.5em')
        .attr('dy', '0.25em');

    svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(windChangeYScale))
        .selectAll('text')
        .style('font-size', '10px');

    svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(pollutionYScale))
        .selectAll('text')
        .style('font-size', '10px');
}
//format date for filename
function formatDate(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

//timeSteps based on calendar date
function updateTimeSteps() {
    const calendarDate = document.getElementById('calendar')._flatpickr.selectedDates[0];
    const formattedDate = formatDate(calendarDate);
    
    return [
        { label: '00:00', file: `board_archive2/board_${formattedDate}_0000-0600.json` },
        { label: '06:00', file: `board_archive2/board_${formattedDate}_0600-1200.json` },
        { label: '12:00', file: `board_archive2/board_${formattedDate}_1200-1800.json` },
        { label: '18:00', file: `board_archive2/board_${formattedDate}_1800-0000.json` }
    ];
}

let currentIndex = 0;
let buttonsRef = [];
let timeSteps = [];

function loadDataWithHighlight(index) {
    timeSteps = updateTimeSteps();
    currentIndex = index;
    loadData(timeSteps[currentIndex].file);

    document.querySelectorAll('.time-btn').forEach((btn, i) => {
        if (i === currentIndex) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const calendarCheck = setInterval(() => {
        if (document.getElementById('calendar')._flatpickr) {
            clearInterval(calendarCheck);
            initChart();
        }
    }, 100);
});

function initChart() {
    document.querySelectorAll('.time-btn').forEach((btn, index) => {
        btn.addEventListener('click', function() {
            loadDataWithHighlight(index);
        });
    });
    
    document.getElementById('calendar')._flatpickr.config.onChange.push(function(selectedDates) {
        // Reset to 00:00 when date changes
        loadDataWithHighlight(0);
    });
    
    loadDataWithHighlight(0);
    
    //auto-cycle
    setInterval(() => {
        currentIndex = (currentIndex + 1) % 4;
        loadDataWithHighlight(currentIndex);
    }, 8000);
}
