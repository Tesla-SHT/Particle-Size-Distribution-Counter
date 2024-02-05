const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const echarts = require('echarts');
const { spawn } = require('child_process');
//Initialize the window
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
  require('@electron/remote/main').initialize()  
  require('@electron/remote/main').enable(win.webContents)  
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

// Process the image
ipcMain.on('process-image', (event, { image, minRadius, maxRadius , scale}) => {
  // Call the Python script and pass the parameters
  const pythonProcess = spawn('python', ['python_script.py', image, minRadius, maxRadius, scale]);

  pythonProcess.stdout.on('data', (data) => {
    const imagePath = data.toString().trim();
    
    // read the diameter data
    const diametersData = fs.readFileSync('diameters.txt', 'utf8');
    const histogramData = diametersData.split('\n').map(Number);

    // send the result to the frontend
    event.sender.send('image-processed', { imagePath});
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });
  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
  });
});
