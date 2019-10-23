# Server
manages the communication with the pi with a serial over socket connection  

serves http rest api & static html / js

get logs
`journalctl --unit python_door`

# Instructions
1. move coopdoor.service to /etc/systemd/system/
2. run `sudo systemctl daemon-reload`
3. add the following line with `crontab -e`
```
0 0 */3 * * cd /home/pi/Projects/coop/server && ./env/bin/python3 schedule.py >> cron.log 2>&1
```
