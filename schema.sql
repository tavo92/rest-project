drop table if exists entries;
drop table if exists users;
create table entries (
  id integer primary key autoincrement,
  name text not null,
  cityName text not null,
  gmt integer not null,
  userid integer not null
);

create table users (
  id integer primary key autoincrement,
  user text not null,
  password text not null
);