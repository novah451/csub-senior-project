const width = 1000;
const height = 300;
const margin = { top: 40, right: 30, bottom: 100, left: 30 }; 
const pollutants = ['pm2_5', 'co', 'o3', 'so2', 'no', 'no2', 'pm10'];
const pollutantFullNames = {
    'pm2_5': 'Particulate Matter at 2.5',
    'co': 'Carbon Monoxide (CO)',
    'o3': 'Harmful Ozone Gas (O3)',
    'so2': 'Sulfur Dioxide (SO2)',
    'no': 'Nitric Oxide (NO)',
    'no2': 'Nitrogen Dioxide (NO2)',
    'pm10': 'Particulate Matte at 10'
};

const colorScale = d3.scaleOrdinal()
    .domain(pollutants)
    .range(['#ffdede','#ffca75', '#ff4d00','#ffd9e8', '#FF9966','#ffe100', '#ff7700']);

const tooltip = d3.select('body')
    .append('div')
    .attr('class', 'tooltip');

const xScale = d3.scaleBand().range([margin.left, width - margin.right]).padding(0.2);
const yScale = d3.scaleLinear().range([height - margin.bottom, margin.top]);

let isBarChart = false;
let isGrouped = true;

function createChart(data) {
    d3.select('#pollution-chart-svg').selectAll('*').remove();

    const svg = d3.select('#pollution-chart-svg')
        .attr('width', width)
        .attr('height', height);

    xScale.domain(data.board.map((d, i) => i));
    yScale.domain([0, d3.max(data.board, d => d3.sum(pollutants.map(p => d[p]))) * 1.3]);

    svg.append('g')
        .attr('transform', `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(xScale).tickFormat(d => `${d + 1}`));

    svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(yScale).ticks(10));

    if (isBarChart) {
        const stack = d3.stack().keys(pollutants)(data.board);
        const groups = svg.selectAll('.group')
            .data(stack)
            .enter()
            .append('g')
            .attr('fill', d => colorScale(d.key));

const bars = groups.selectAll('rect')
    .data(d => d)
    .enter()
    .append('rect')
    .attr('x', (d, i) => xScale(i))
    .attr('y', d => yScale(d[1])) // starting y-coordinate
    .attr('height', d => {
        const barHeight = yScale(d[0]) - yScale(d[1]);
        return barHeight < 0 ? 0 : barHeight; // ensure height is non-negative
    })
    .attr('width', xScale.bandwidth());

        function toggleBarType() {
            bars.transition().duration(5000)
                .attr('x', (d, i) => isGrouped ? xScale(i) + (xScale.bandwidth() / pollutants.length) * pollutants.indexOf(d.key) : xScale(i))
                .attr('width', isGrouped ? xScale.bandwidth() / pollutants.length : xScale.bandwidth());
            isGrouped = !isGrouped;
        }

        setInterval(toggleBarType, 1000);
    } else {
        pollutants.forEach(pollutant => {
            const area = d3.area()
                .x((d, i) => xScale(i) + xScale.bandwidth() / 2)
                .y0(yScale(0)) 
                .y1(d => yScale(d[pollutant])); 
    
            svg.append('path')
                .datum(data.board)
                .attr('class', 'area')
                .attr('fill', colorScale(pollutant))
                .attr('d', area);
            const line = svg.append('path')
                .datum(data.board)
                .attr('class', 'line')
                .attr('stroke', colorScale(pollutant))
                .attr('stroke-width', 2)
                .attr('fill', 'none')
                .attr('d', d3.line()
                    .x((d, i) => xScale(i) + xScale.bandwidth() / 2)
                    .y(d => yScale(d[pollutant])));
    
            const totalLength = line.node().getTotalLength();
            line
                .attr('stroke-dasharray', totalLength)
                .attr('stroke-dashoffset', totalLength)  
    
            function animateLine() {
                line.transition()
                    .duration(10000) 
                    .ease(d3.easeLinear) 
                    .attr('stroke-dashoffset', 0) 
                    .on('end', function() {
                        d3.select(this)
                            .attr('stroke-dashoffset', totalLength);
                        animateLine(); 
                    });
            }
    
            animateLine();
    
            svg.selectAll(`.dot-${pollutant}`)
                .data(data.board)
                .enter()
                .append('circle')
                .attr('class', `dot-${pollutant}`)
                .attr('cx', (d, i) => xScale(i) + xScale.bandwidth() / 2)
                .attr('cy', d => yScale(d[pollutant]))
                .attr('r', 4)
                .attr('fill', colorScale(pollutant))
                .on('mouseover', function(event, d) {
                    tooltip.transition().duration(200).style('opacity', .9);
                    tooltip.html(`${pollutant}: ${d[pollutant]}`)
                        .style('left', `${event.pageX + 5}px`)
                        .style('top', `${event.pageY - 28}px`);
                })
                .on('mouseout', function() {
                    tooltip.transition().duration(200).style('opacity', 0);
                });
        });
    }
    const legend = svg.append('g')
        .attr('transform', `translate(${width - margin.right + 20}, ${margin.top})`);

    legend.selectAll('.legend-item')
        .data(pollutants)
        .enter()
        .append('g')
        .attr('class', 'legend-item')
        .attr('transform', (d, i) => `translate(0, ${i * 20})`) 
        .each(function(d, i) {
            d3.select(this).append('rect')
                .attr('width', 15)
                .attr('height', 15)
                .attr('fill', colorScale(d));

            d3.select(this).append('text')
                .attr('x', 20)
                .attr('y', 12)
                .text(pollutantFullNames[d])  
                .style('font-size', '12px')
                .style('fill', '#fff');
        });
}

function updateChart() {
    fetch('board.json')
        .then(response => response.json())
        .then(data => createChart(data))
        .catch(error => console.error('Error loading data:', error));
}

document.getElementById('chart-toggle').addEventListener('change', () => {
    isBarChart = !isBarChart;
    updateChart();
});
updateChart();
setInterval(() => {
    const chartToggleElement = document.getElementById('chart-toggle');
    chartToggleElement.checked = !chartToggleElement.checked;  
    isBarChart = chartToggleElement.checked; 
    updateChart();  
}, 100000);  
