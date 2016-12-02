CREATE DATABASE photoshare;
USE photoshare;
DROP TABLE Users CASCADE;
DROP TABLE Friends CASCADE;
DROP TABLE Pictures CASCADE;
DROP TABLE Albums CASCADE;
DROP TABLE Album_Contents CASCADE;
DROP TABLE Likes CASCADE;
DROP TABLE Comments CASCADE;
DROP TABLE Tags CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
	firstname varchar(255),
	lastname varchar(255),
	DOB date,
	hometown varchar(255),
	gender varchar(255),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Friends (
	user1 integer NOT NULL,
	user2 integer NOT NULL,
	CONSTRAINT friendship_pk PRIMARY KEY (user1, user2),
	CONSTRAINT user1_fk FOREIGN KEY (user1) REFERENCES Users(user_id),
	CONSTRAINT user2_fk FOREIGN KEY (user2) REFERENCES Users(user_id)	
);

CREATE TABLE Pictures
(
  picture_id int4 AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Albums (
	album_id integer NOT NULL AUTO_INCREMENT,
	owner_id integer NOT NULL,
	name varchar(45) NOT NULL,
	date_of_creation date NOT NULL,
	CONSTRAINT album_id_pk PRIMARY KEY (album_id),
	CONSTRAINT owner_id_fk2 FOREIGN KEY (owner_id) REFERENCES Users(user_id)
);


CREATE TABLE Album_Contents (
	album_id integer NOT NULL,
	picture_id integer NOT NULL,
	CONSTRAINT album_contains_pk PRIMARY KEY (album_id, picture_id),
	CONSTRAINT album_id_fk FOREIGN KEY (album_id) REFERENCES Albums(album_id),
	CONSTRAINT picture_id_fk FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id)
);

CREATE TABLE Likes(
	user_id integer NOT NULL,
	picture_id integer NOT NULL,
	CONSTRAINT likes_pk PRIMARY KEY (user_id, picture_id),
	CONSTRAINT user_id_fk FOREIGN KEY (user_id) REFERENCES Users(user_id),
	CONSTRAINT picture_id_fk2 FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id)
);

CREATE TABLE Comments(
	comment_id integer NOT NULL AUTO_INCREMENT,
	owner_id integer NOT NULL,
	picture_id integer,
	text varchar(255),
	dateofcomment date NOT NULL,
	CONSTRAINT commentid_pk PRIMARY KEY (comment_id),
	CONSTRAINT ownerid_fk2 FOREIGN KEY (owner_id) REFERENCES Users(user_id),
	CONSTRAINT picture_id_fk3 FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id)
);

CREATE TABLE Tags(
	picture_id integer NOT NULL,
	tag_id integer NOT NULL AUTO_INCREMENT,
	tag varchar(100) UNIQUE,
	CONSTRAINT tags_pk PRIMARY KEY (tag_id),
	CONSTRAINT picture_id_fk4 FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id)
)
