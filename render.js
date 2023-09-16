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
imageInput.addEventListener('change', (event) => {
    console.log(event.target.files[0]);
    const filePath = event.target.files[0].path;
    console.log(filePath);
    image = filePath;
    console.log(`Selected image: ${image}`);
    // 在选择新文件时先移除旧的图片
    resultDiv.removeChild(img);
    //删除scale,Count,minRadius,maxRadius输入数据
    Scale.value = '';
    Count.value = '';
    minRadiusInput.value = '';
    maxRadiusInput.value = '';
    // 更新图片的 src 属性
    img.src = image; // 清空旧的图片 src 属性
    // 在选择新文件时先清空柱状图容器和柱状图实例
    if (chart) {
        chart.clear(); // 清空柱状图实例的所有内容
        chart = null; // 重置柱状图实例变量
    }
});

processButton.addEventListener('click', () => {
    const minRadius = parseInt(minRadiusInput.value);
    const maxRadius = parseInt(maxRadiusInput.value);
    const scale = parseInt(Scale.value);
    const count = parseInt(Count.value);
    if (!image) {
        alert('Please select an image first.');
        return;
    }

    // 向主进程发送事件，以启动图像处理
    ipcRenderer.send('process-image', { image, minRadius, maxRadius ,scale});
});

// 监听主进程传回的处理结果
ipcRenderer.on('image-processed', (event, { imagePath, histogramData }) => {
    img.src = imagePath;
    console.log(img.src);
    resultDiv.innerHTML = '';
    resultDiv.appendChild(img);
    // 读取 diameters.txt 文件内容
    fs.readFile('diameters.txt', 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading diameters.txt:', err);
            return;
        }
        // 输入的最小半径和最大半径
        let minRadius = 2 * parseFloat(document.getElementById('minRadius').value);
        let maxRadius = 2 * parseFloat(document.getElementById('maxRadius').value);
        chart = echarts.init(document.getElementById('barChart'));
        // 将数据拆分为数组，假设数据每行一个数值
        const diameterData = data.split('\n').map(Number);
        const scalevalue = diameterData[0]
        // 定义区间宽度
        const count = parseInt(Count.value);
        const intervalWidth = count; // 可以根据需要调整区间宽度
        // 去除第一个元素
        diameterData.slice(1);
        // 计算最小值和最大值
        //minRadius*=scalevalue;
        //maxRadius*=scalevalue;
        if (minRadius<Math.min(...diameterData)){
            minRadius=Math.min(...diameterData);
        }
        if (maxRadius>Math.max(...diameterData)){
            maxRadius=Math.max(...diameterData);
        }
        const intervalCount = Math.ceil((maxRadius - minRadius) / intervalWidth);

        console.log(minRadius,maxRadius,intervalWidth, intervalCount);

        // 生成直径区间数组
        const diameterRanges = [];
        for (let i = 0; i < intervalCount; i++) {
            const start = minRadius + i * intervalWidth;
            const end = minRadius + (i + 1) * intervalWidth;
            diameterRanges.push(`${start.toFixed(2)}~${end.toFixed(2)}`);
        }
        console.log(diameterRanges)
        // 初始化每个区间的数量为0
        const intervalCounts = new Array(intervalCount).fill(0);
        // 假设 diameterData 是一个包含直径值的数组
        for (const diameter of diameterData) {
            for (let i = 0; i < intervalCount; i++) {
                const [min, max] = diameterRanges[i].split('~').map(parseFloat);
                if (diameter >= min && diameter < max) {
                    intervalCounts[i]++;
                    break; // 跳出内循环，避免将数据分配到多个区间
                }
            }
        }

        // 创建柱状图实例
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
                data: diameterRanges, // 使用区间范围作为 x 坐标的数据
            },
            yAxis: {
                type: 'value',
                name: 'Frequency',
            },
            series: [{
                name: 'Frequency',
                type: 'bar',
                data: histogramData, // 使用直方图数据数组
                barWidth: '60%',
                itemStyle: {
                    color: 'rgba(75, 192, 192, 0.6)',
                }
            }]
        };

        chart.setOption(option);

    });
});

