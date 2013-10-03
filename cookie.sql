drop table if exists cookies;
create table cookies (
	id integer primary key autoincrement,
	username text not null,
	session_id text not null
);
