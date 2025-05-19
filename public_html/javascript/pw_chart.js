function loadData(file) {
    d3.json(file).then(data => {
        createCombinedChart(data);
    }).catch(error => {
        console.error('Error loading the JSON file:', error);
    });
}

function addLegend(svg, width, margin) {
    const windChangeColors = {
        "10u_wind_change": "#00e5ff",  // Light cyan
        "10v_wind_change": "#00bcd4",  // Medium cyan (Material Design)
        "u_wind_change":   "#00acc1",  // Deeper cyan
        "v_wind_change":   "#0097a7"   // Darker cyan
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

    const windChangeFullNames = {
        "10u_wind_change": "10U Wind Changes",
        "10v_wind_change": "10V Wind Changes",
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
        'pm10': 'Particulate Matte at 10'
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

    const buttonContainer = svg.append('g')
        .attr('transform', `translate(${width / 2 - 100}, 10)`);

    const buttonData = [
        { label: '00:00', file: 'board_2024-03-04-00-06.json' },
        { label: '06:00', file: 'board_2024-03-04-06-12.json' },
        { label: '12:00', file: 'board_2024-03-04-12-18.json' },
        { label: '18:00', file: 'board_2024-03-04-18-00.json' }
    ];

    buttonContainer.selectAll('.button')
        .data(buttonData)
        .enter()
        .append('foreignObject')
        .attr('x', (d, i) => i * 90)
        .attr('y', 0)
        .attr('width', 70)
        .attr('height', 30)
        .append('xhtml:button')
        .attr('class', 'button')
        .style('font-size', '11px')
        .style('padding', '4px 8px')
        .style('width', '100%')
        .text(d => d.label)
        .on('click', (event, d) => loadDataWithHighlight(buttonData.indexOf(d)));

    const windChangeColors = {
"10u_wind_change": "#00ffff",  // Cyan
"10v_wind_change": "#00bfff",  // Sky blue
"u_wind_change":   "#0077ff",  // Vivid blue
"v_wind_change":   "#002b80"   // Dark navy blue

    };

    const pollutionColors = {
        "co": "#FFA500", "no": "#FF8C00", "no2": "#FF6347", "o3": "#FF4500", "so2": "#FF0000", "pm2_5": "#B22222", "pm10": "#8B0000"
    };

    const xScale = d3.scaleLinear().domain([0, data.board.length - 1]).range([margin.left, width - margin.right]);
    const p_XScale = xScale;

    const windChangeYScale = d3.scaleLinear()
        .domain([
            d3.min(data.board, d => Math.min(d["10u_wind_change"], d["10v_wind_change"], d["u_wind_change"], d["v_wind_change"])),
            d3.max(data.board, d => Math.max(d["10u_wind_change"], d["10v_wind_change"], d["u_wind_change"], d["v_wind_change"]))
        ])
        .range([height / 2 - 20, margin.top + 20]);

    const pollutionYScale = d3.scaleLinear()
        .domain([
            0,
            d3.max(data.board, d => Math.max(d["co"], d["no"], d["no2"], d["o3"], d["so2"], d["pm2_5"], d["pm10"]))
        ])
        .range([height - margin.bottom, height / 2 + 20]);

    const tooltip = d3.select('body').append('div')
        .attr('class', 'tooltip')
        .style('font-size', '12px')
        .style('padding', '6px');

    Object.keys(windChangeColors).forEach(key => {
        svg.append('path')
            .datum(data.board)
            .attr('fill', windChangeColors[key])
            .attr('opacity', 0.25)
            .attr('d', d3.area()
                .x((d, i) => xScale(i))
                .y0(windChangeYScale(0))
                .y1(d => windChangeYScale(d[key]))
                .curve(d3.curveCatmullRom));

        const line = svg.append('path')
            .datum(data.board)
            .attr('stroke', windChangeColors[key])
            .attr('stroke-width', 1.5)
            .attr('fill', 'none')
            .attr('d', d3.line()
                .x((d, i) => xScale(i))
                .y(d => windChangeYScale(d[key]))
                .curve(d3.curveCatmullRom));

        const len = line.node().getTotalLength();
        line.attr('stroke-dasharray', `${len} ${len}`)
            .attr('stroke-dashoffset', len)
            .transition()
            .duration(4000)
            .attr('stroke-dashoffset', 0);
    });

    Object.keys(pollutionColors).forEach((key) => {
        const barWidth = (width - margin.left - margin.right) / data.board.length;
        svg.selectAll(`.pollution_${key}`)
            .data(data.board)
            .enter()
            .append('rect')
            .attr('x', (d, i) => p_XScale(i))
            .attr('y', d => pollutionYScale(d[key]))
            .attr('width', barWidth - 1)
            .attr('height', d => Math.max(0, height - margin.bottom - pollutionYScale(d[key])))

            .attr('fill', pollutionColors[key])
            .on('mouseover', (event, d) => {
                tooltip.style('opacity', 1)
                    .html(`${key.toUpperCase()}: ${d[key].toFixed(4)}`)
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
        .call(d3.axisBottom(xScale).tickFormat(i => data.board[i].center))
        .selectAll('text')
        .style('font-size', '10px')
        .attr('dx', '-0.5em')
        .attr('dy', '0.25em');

    svg.append('g')
        .attr('transform', `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(p_XScale).tickFormat(i => data.board[i].center))
        .selectAll('text')
        .style('font-size', '10px')
        .attr('dx', '-0.5em')
        .attr('dy', '0.25em');

    svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(windChangeYScale)).selectAll('text').style('font-size', '10px');

    svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(pollutionYScale)).selectAll('text').style('font-size', '10px');
}

const timeSteps = [
    { label: '00:00', file: 'board_2024-03-04-00-06.json' },
    { label: '06:00', file: 'board_2024-03-04-06-12.json' },
    { label: '12:00', file: 'board_2024-03-04-12-18.json' },
    { label: '18:00', file: 'board_2024-03-04-18-00.json' }
];

let currentIndex = 0;
let buttonsRef = [];

function loadDataWithHighlight(index) {
    currentIndex = index;
    loadData(timeSteps[currentIndex].file);

    setTimeout(() => {
        buttonsRef.forEach((btn, i) => {
            btn.classed('active', i === currentIndex);
        });
    }, 100);
}

loadDataWithHighlight(currentIndex);

setInterval(() => {
    currentIndex = (currentIndex + 1) % timeSteps.length;
    loadDataWithHighlight(currentIndex);
}, 5000);

const originalCreate = createCombinedChart;
createCombinedChart = function (data) {
    originalCreate(data);
    buttonsRef = [];
    d3.selectAll('.button').each(function () {
        buttonsRef.push(d3.select(this));
    });
    buttonsRef.forEach((btn, i) => {
        btn.classed('active', i === currentIndex);
        btn.on('click', () => loadDataWithHighlight(i));
    });
};
