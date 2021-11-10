create table if not exists podcast (
  podcast_id serial primary key,
  name varchar(255) not null unique
);

insert into podcast (name) values 
  ('Papo De Parceiro'),
  ('Caneca De Mamicas'),
  ('Generacast'),
  ('Extra'),
  ('Empreendedor'),
  ('La Do Bunker'),
  ('Nerdcash'),
  ('Nerdcast'),
  ('Nerdtech'),
  ('Speak English');

create table if not exists person (
  person_id serial primary key,
  name varchar(255) not null unique,
  url varchar(2048),
  photo_url varchar(2048) unique
);

create table if not exists podcast_host (
  podcast_host_id serial primary key,
  podcast_id integer references podcast(podcast_id) not null,
  host_id integer references person(person_id) not null,
  unique (podcast_id, host_id)
);

create table if not exists episode (
  episode_id serial primary key, 
  little_thumb_url varchar(2048) not null,
  big_thumb_url varchar(2048) not null,
  podcast_id integer references podcast(podcast_id) not null,
  number integer unique,
  title varchar(255) not null unique, 
  length time not null,
  date date not null, 
  audio_url varchar(2048) not null unique,
  content_text text
);

create table if not exists episode_guest (
  episode_guest_id serial primary key,
  episode_id integer references episode(episode_id) not null,
  guest_id integer references person(person_id) not null,
  unique (episode_id, guest_id)
);

create table if not exists episode_url (
  episode_url_id serial primary key,
  episode_id integer references episode(episode_id) not null,
  url varchar(2048) not null unique
);
