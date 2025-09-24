PRAGMA foreign_keys = ON;

-- Drop tables if they exist (helpful for dev/testing)
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS following;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
    username   VARCHAR(20)  PRIMARY KEY NOT NULL,
    fullname   VARCHAR(40)  NOT NULL,
    email      VARCHAR(40)  NOT NULL,
    filename   VARCHAR(64)  NOT NULL,
    password   VARCHAR(256) NOT NULL,
    created    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Posts table
CREATE TABLE posts (
    postid   INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    filename VARCHAR(64)  NOT NULL,
    owner    VARCHAR(20)  NOT NULL,
    created  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner) REFERENCES users(username) ON DELETE CASCADE
);

-- Following table
CREATE TABLE following (
    follower VARCHAR(20) NOT NULL,
    followee VARCHAR(20) NOT NULL,
    created  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower, followee),
    FOREIGN KEY(follower) REFERENCES users(username) ON DELETE CASCADE,
    FOREIGN KEY(followee) REFERENCES users(username) ON DELETE CASCADE
);

-- Comments table
CREATE TABLE comments (
    commentid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    owner     VARCHAR(20) NOT NULL,
    postid    INTEGER     NOT NULL,
    text      VARCHAR(1024) NOT NULL,
    created   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner) REFERENCES users(username) ON DELETE CASCADE,
    FOREIGN KEY(postid) REFERENCES posts(postid) ON DELETE CASCADE
);

-- Likes table
CREATE TABLE likes (
    likeid  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    owner   VARCHAR(20) NOT NULL,
    postid  INTEGER     NOT NULL,
    created DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner) REFERENCES users(username) ON DELETE CASCADE,
    FOREIGN KEY(postid) REFERENCES posts(postid) ON DELETE CASCADE
);
