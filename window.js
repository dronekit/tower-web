var app = require('app');  // Module to control application life.
var BrowserWindow = require('browser-window');  // Module to create native browser window.

// Report crashes to our server.
require('crash-reporter').start();

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the javascript object is GCed.
var mainWindow = null;

// Quit when all windows are closed.
app.on('window-all-closed', function() {
  if (process.platform != 'darwin') {
    app.quit();
  }
});

function launch (args, next) {
  var spawn = require('child_process').spawn;
  var p = spawn(args[0], args.slice(1), {
    cwd: __dirname,
    stdio: 'inherit',
  })
  setTimeout(next, 500, p);
}

// This method will be called when Electron has done everything
// initialization and ready for creating browser windows.
app.on('ready', function() {
  // Create the browser window.
  launch(['script', '-q', '/dev/null', 'python', 'tower'].concat(process.argv.slice(2)), function (proc) {
    proc.on('exit', function (code) {
      process.exit(code);
    })

    mainWindow = new BrowserWindow({width: 1000, height: 800});

    // and load the index.html of the app.
    mainWindow.loadUrl('http://localhost:24403/');

    // Open the devtools.
    // mainWindow.openDevTools();

    // Emitted when the window is closed.
    mainWindow.on('closed', function() {
      // Dereference the window object, usually you would store windows
      // in an array if your app supports multi windows, this is the time
      // when you should delete the corresponding element.
      proc.kill('SIGTERM');
      mainWindow = null;
    });
  });
});
