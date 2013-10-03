drop table if exists users;
drop table if exists playlist;
drop table if exists belong;
create table users (
	id integer primary key autoincrement,
	name text not null,
	hash text not null,
	salt text not null
);
create table playlist (
	id integer primary key autoincrement,
	name text not null,
	owner text not null
);
create table belong (
	song integer,
	playlist integer
);
