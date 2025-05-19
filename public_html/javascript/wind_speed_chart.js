function createChart(data) {
    const width = 1000;
    const height = 300;
    const margin = { top: 40, right: 30, bottom: 120, left: 30 }; 

    const svg = d3.select('#svgId')
                  .attr('width', width)
                  .attr('height', height);

	console.log();

    const xScale = d3.scaleLinear()
                     .domain([0, data.board.length - 1])
                     .range([margin.left, width - margin.right]);

    const yScale = d3.scaleLinear()
                     .domain([
                         d3.min(data.board, d => Math.min(
                             d["10u_wind_change"],
                             d["10v_wind_change"],
                             d["u_wind_change"],
                             d["v_wind_change"],
                             d["specific_humidity_change"]
                         )),
                         d3.max(data.board, d => Math.max(
                             d["10u_wind_change"],
                             d["10v_wind_change"],
                             d["u_wind_change"],
                             d["v_wind_change"],
                             d["specific_humidity_change"]
                         ))
                     ])
                     .range([height - margin.bottom, margin.top]);

    const colors = {
        "10u_wind_change": "#e0f8ff",
        "10v_wind_change": "#c9f3ff",
        "u_wind_change": "#a8ecff",
        "v_wind_change": "#52d9ff",
        "specific_humidity_change": "#407382"
    };

    const tooltip = d3.select('body').append('div')
                      .attr('class', 'tooltip');

    const areaGenerator = key =>
        d3.area()
            .x((d, i) => xScale(i))
            .y0(yScale(0))
            .y1(d => yScale(d[key]))
            .curve(d3.curveCatmullRom);

    const lineGenerator = key =>
        d3.line()
            .x((d, i) => xScale(i))
            .y(d => yScale(d[key]))
            .curve(d3.curveCatmullRom);

    svg.selectAll('*').remove();  

    Object.keys(colors).forEach(key => {
        const area = svg.append('path')
            .datum(data.board)
            .attr('class', 'area')
            .attr('fill', colors[key])
            .attr('opacity', 0.25)
            .attr('d', areaGenerator(key))
            .on('mouseover', function () {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('opacity', 0.5); 
            })
            .on('mouseout', function () {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('opacity', 0.25);
            });
	    console.log();

        const path = svg.append('path')
            .datum(data.board)
            .attr('class', 'line')
            .attr('stroke', colors[key])
            .attr('d', lineGenerator(key));

        const totalLength = path.node().getTotalLength();

        path.attr('stroke-dasharray', `${totalLength} ${totalLength}`)
            .attr('stroke-dashoffset', totalLength)
            .transition()
            .duration(10000)  // Slow down 4 seconds
            .ease(d3.easeCubicInOut)
            .attr('stroke-dashoffset', 0);

        svg.selectAll(`circle.data_${key.replace('.', '_')}`)
            .data(data.board)
            .enter()
            .append('circle')
            .attr('cx', (d, i) => xScale(i))
            .attr('cy', d => yScale(d[key]))
            .attr('r', 4)
            .attr('fill', colors[key])
            .on('mouseover', (event, d) => {
                tooltip.style('opacity', 1)
                       .html(`${key}: ${d[key].toFixed(2)}`)
                       .style('left', `${event.pageX + 10}px`)
                       .style('top', `${event.pageY - 20}px`);

                d3.select(event.target)
                    .transition()
                    .duration(100)
                    .attr('r', 6);
            })
            .on('mouseout', (event) => {
                tooltip.style('opacity', 0);

                d3.select(event.target)
                    .transition()
                    .duration(100)
                    .attr('r', 4);
            });
    });

    svg.append('g')
        .attr('transform', `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(xScale).tickFormat(i => data.board[i].center));

    svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(yScale));

    const legend = svg.append('g')
                      .attr('transform', `translate(${width - 10}, ${margin.top})`);

    Object.keys(colors).forEach((key, i) => {
        legend.append('rect')
              .attr('x', 0)
              .attr('y', i * 25)
              .attr('width', 15)
              .attr('height', 15)
              .attr('fill', colors[key]);

        legend.append('text')
              .attr('x', 25)
              .attr('y', i * 25 + 12)
              .text(key)
              .style('font-size', '14px')
              .style('fill', 'white') // Set text color to white
              .attr('alignment-baseline', 'middle');
          
    });
}

function updateChart() {
    d3.json('board.json').then(data => {
        createChart(data);  
    });
}

updateChart();
setInterval(updateChart, 11000);
