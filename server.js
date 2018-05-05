const SerialPort = require('serialport');
const port = new SerialPort('/dev/ttyACM0', { baudRate: 9600 });
const { Database } = require('sqlite3');

const db = new Database('./database');
// `create table if not exists temps ();`
db.run(`create table if not exists temps (temp Integer, date Integer);`);

port.on('open', function() {
  let last = '';
  port.on('data', function(data) {
    last += data.toString()
    const date = Date.now();
    const arr = last.split('\r\n');
    let add;
    ([add, last] = [arr.slice(0, -1).map(v => Math.floor(parseFloat(v)*100)), arr.slice(-1)[0]])
    if (add.length > 0) {
      db.run(`insert into temps values ${add.map(temp => `(${temp},${date})`).join(',')};`);
    }
  });
});
