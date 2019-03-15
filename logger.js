const dgram = require('dgram');
const server = dgram.createSocket('udp4');
const fs = require('fs');

server.on('message', (msg, rinfo) => {
    fs.appendFileSync("log.txt",new Date().toISOString()+msg+"\n")
});

server.bind(9100);
// server listening 0.0.0.0:9100