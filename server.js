const SerialPort = require('serialport');
const path = require('path');
const { Database } = require('sqlite3');
const http = require('http');
const express = require('express');
const WebSocket = require('ws');

const app = express();
const port = new SerialPort('/dev/ttyACM0', { baudRate: 9600 });

const db = new Database(path.join(__dirname, 'database'));
// `create table if not exists temps ();`
db.run(`create table if not exists temps (temp Integer, date Integer);`);

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

      wss.clients
        .forEach(client => client.readyState === WebSocket.OPEN ?
          client.send(JSON.stringify({ temp, date })) :
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
