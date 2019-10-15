#select value, strftime('%d-%m-%Y %H:%M', datetime(date, 'unixepoch', 'localtime')) from requests;
#sqlite3 test.db "select (date*1.0-strftime('%s', 'now'))/3600 from requests";
select datetime(date, 'unixepoch', 'localtime') from requests where textstate=="scheduled" limit 1;
