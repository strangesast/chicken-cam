# Chick Coop Door
A project to control a chicken coop door based on a regular schedule (sunrise / sunset) and as required.
# Service
move python file to
`/usr/local/lib/python_door_service`


get logs
`journalctl --unit python_door`


add the following line to cron with `crontab -e`
```
0 0 */3 * * cd /home/pi/Projects/coop/server && ./env/bin/python3 schedule.py >> cron.log 2>&1
```
