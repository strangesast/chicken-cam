var SerialPort = require('serialport');
var port = new SerialPort('/dev/ttyACM0', { baudRate: 9600 });

port.on('open', function() {
  let last = '';
  port.on('data', function(data) {
    last += data.toString()
    const arr = last.split('\r\n');
    if (arr[arr.length - 1] === '') {
      console.log(arr.slice(0, arr.length - 1))
      last = arr.slice(arr.length - 1).join('\r\n');
    }
  });
});
