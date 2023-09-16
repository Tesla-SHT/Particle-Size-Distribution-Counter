const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const echarts = require('echarts');
const { spawn } = require('child_process');

function createWindow() {
  const win = new BrowserWindow({
    width: 1500,
    height: 1200,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
  });
  require('@electron/remote/main').initialize()  //添加语句
  require('@electron/remote/main').enable(win.webContents)   //添加语句
  win.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
// 处理图像的功能
ipcMain.on('process-image', (event, { image, minRadius, maxRadius , scale}) => {
  // 调用Python脚本并传递参数
  const pythonProcess = spawn('python', ['python_script.py', image, minRadius, maxRadius, scale]);

  pythonProcess.stdout.on('data', (data) => {
    const imagePath = data.toString().trim();
    
    // 读取直径数据
    const diametersData = fs.readFileSync('diameters.txt', 'utf8');
    const histogramData = diametersData.split('\n').map(Number);

    // 发送处理结果到前端
    event.sender.send('image-processed', { imagePath});
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
  });
});
