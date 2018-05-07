const SerialPort = require('serialport');
const path = require('path');
const { Database } = require('sqlite3');
const http = require('http');
const express = require('express');
const WebSocket = require('ws');

const app = express();
const port = new SerialPort('/dev/ttyACM0', { baudRate: 9600 });

const db = new Database(path.join(__dirname, 'database'));
let lastValue;
// `create table if not exists temps ();`
db.run(`create table if not exists temps (inside Integer, outside Integer, date Integer);`);

if (process.env.NODE_ENV !== 'production') {
  app.get('/', (_, res) => {
    res.sendFile(path.join(__dirname, 'static', 'index.html'));
  });
}

app.get('/api', (req, res, next) => {
  if (req.accepts('text/html')) {
    db.all(`select * from temps order by date desc`, (err, rows) => {
      if (err != null) {
        next(err);
        return;
      }
      res.send(`<pre>${JSON.stringify(rows, null, 2)}</pre>`);
    });
  } else if (req.accepts('application/stream+json')) {
    db.each(
      `select * from temps order by date desc`,
      (err, row) => {
        if (err) {
          next(err);
          return;
        }
        res.write(`${JSON.stringify(row)}\n`);
      },
      (err, n) => {
        res.end();
      },
    );
  } else {
    db.all(`select * from temps order by date desc`, (err, rows) => {
      if (err != null) {
        next(err);
        return;
      }
      res.json(rows);
    });
  }
});

app.get('/api/status', (_, res) => {
  res.json({ open: port.isOpen });
});

let first = true;

port.on('open', function() {
  let last = '';
  port.on('data', function(data) {
    last += data.toString()
    let arr = last.split('\r\n');
    // dump first response
    console.log(first, arr);
    if (first) {
      if (arr.length > 1) {
        arr = arr.slice(1);
        first = false;
      } else {
        return;
      }
    }
    let add;
    ([add, last] = [arr.slice(0, -1), arr.slice(-1)[0]])
    const date = Date.now();
    console.log('add', add);
    for (const temps of add) {
      const [inside, outside] = temps.split(',').map(v => Math.floor(parseFloat(v)*100));
      lastValue = { inside, outside, date };
      db.run(`insert into temps values (${[inside, outside, date].join(',')})`);
      wss.clients
        .forEach(client => client.readyState === WebSocket.OPEN ?
          client.send(JSON.stringify({ inside, outside, date })) :
          null
        );
    }
  });
});

port.on('error', e => console.error(`port error: ${ e }`));

const PORT = 3000;

const server = http.createServer(app);

const wss = new WebSocket.Server({ server, path: '/api/sockets' });

wss.on('connection', ws => {
  ws.on('message', () => {

  });
});

server.listen(PORT, () => {
  console.log(`listening on ${PORT}`);
});
