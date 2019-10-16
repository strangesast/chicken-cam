#sqlite3 test.db "select value, strftime('%d-%m-%Y %H:%M', datetime(date, 'unixepoch', 'localtime')) from requests;"
#sqlite3 test.db "select (date*1.0-strftime('%s', 'now'))/3600 from requests;"
#sqlite3 test.db "select datetime(date, 'unixepoch', 'localtime') from requests where textstate=="scheduled" limit 1;"
sqlite3 test.db "select datetime(date, 'unixepoch', 'localtime'), case when sidesensor==0 and bottomsensor=1 then 'OPEN' when sidesensor==1 and bottomsensor==0 then 'CLOSED' else 'UNKNOWN' end 'text' from events_states order by date desc limit 1;"
