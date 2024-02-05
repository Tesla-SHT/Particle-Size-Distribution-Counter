const fs = require('fs');
const electron = require('electron');
const echarts = require('echarts');
const { ipcRenderer } = electron;

let Scale=document.getElementById('scale');
let Count=document.getElementById('Count');
const imageInput = document.getElementById('imageInput');
let minRadiusInput = document.getElementById('minRadius');
let maxRadiusInput = document.getElementById('maxRadius');
const processButton = document.getElementById('processButton');
let resultDiv = document.getElementById('result');

let image = null;
let img = document.createElement('img');
let chart = null;
//Clear the input when changing the image
imageInput.addEventListener('change', (event) => {
    console.log(event.target.files[0]);
    const filePath = event.target.files[0].path;
    console.log(filePath);
    image = filePath;
    console.log(`Selected image: ${image}`);
    resultDiv.removeChild(img);
    Scale.value = '';
    Count.value = '';
    minRadiusInput.value = '';
    maxRadiusInput.value = '';
    img.src = image; 
    if (chart) {
        chart.clear();
        chart = null; 
    }
});
//Sends image processing events to the main process
processButton.addEventListener('click', () => {
    const minRadius = parseInt(minRadiusInput.value);
    const maxRadius = parseInt(maxRadiusInput.value);
    const scale = parseInt(Scale.value);
    const count = parseInt(Count.value);
    if (!image) {
        alert('Please select an image first.');
        return;
    }

    ipcRenderer.send('process-image', { image, minRadius, maxRadius ,scale});
});

// Process the results returned by the main process
ipcRenderer.on('image-processed', (event, { imagePath, histogramData }) => {
    img.src = imagePath;
    console.log(img.src);
    resultDiv.innerHTML = '';
    resultDiv.appendChild(img);
    fs.readFile('diameters.txt', 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading diameters.txt:', err);
            return;
        }
        let minRadius = 2 * parseFloat(document.getElementById('minRadius').value);
        let maxRadius = 2 * parseFloat(document.getElementById('maxRadius').value);
        chart = echarts.init(document.getElementById('barChart'));
        const diameterData = data.split('\n').map(Number);
        const scalevalue = diameterData[0]
        const count = parseInt(Count.value);
        const intervalWidth = count; 
        diameterData.slice(1);
        if (minRadius<Math.min(...diameterData)){
            minRadius=Math.min(...diameterData);
        }
        if (maxRadius>Math.max(...diameterData)){
            maxRadius=Math.max(...diameterData);
        }
        const intervalCount = Math.ceil((maxRadius - minRadius) / intervalWidth);

        const diameterRanges = [];
        for (let i = 0; i < intervalCount; i++) {
            const start = minRadius + i * intervalWidth;
            const end = minRadius + (i + 1) * intervalWidth;
            diameterRanges.push(`${start.toFixed(2)}~${end.toFixed(2)}`);
        }
        const intervalCounts = new Array(intervalCount).fill(0);
        
        for (const diameter of diameterData) {
            for (let i = 0; i < intervalCount; i++) {
                const [min, max] = diameterRanges[i].split('~').map(parseFloat);
                if (diameter >= min && diameter < max) {
                    intervalCounts[i]++;
                    break; 
                }
            }
        }

        // Create the bar chart
        const histogramData = intervalCounts;
        console.log(histogramData)
        console.log(diameterRanges)
        const option = {
            title: {
                text: 'Colony Diameter Distribution',
                x: 'center'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            xAxis: {
                type: 'category',
                data: diameterRanges, 
            },
            yAxis: {
                type: 'value',
                name: 'Frequency',
            },
            series: [{
                name: 'Frequency',
                type: 'bar',
                data: histogramData,
                barWidth: '60%',
                itemStyle: {
                    color: 'rgba(75, 192, 192, 0.6)',
                }
            }]
        };

        chart.setOption(option);
    });
});

