DROP TABLE IF EXISTS users cascade;
DROP TABLE IF EXISTS ingredients cascade;
DROP TABLE IF EXISTS categories cascade;
DROP TABLE IF EXISTS pantries cascade;
DROP TABLE IF EXISTS cookbooks cascade;
DROP TABLE IF EXISTS recipes cascade;
DROP TABLE IF EXISTS shoppinglists cascade;
DROP TABLE IF EXISTS recipescontain;
DROP TABLE IF EXISTS shoplistcontain;
DROP TABLE IF EXISTS pantriescontain;
DROP TABLE IF EXISTS recipecategories;
DROP TABLE IF EXISTS cookbookcontents;
DROP TABLE IF EXISTS cookbookowners;
DROP TABLE IF EXISTS reciperatings;

CREATE TABLE recipes(
    recid serial primary key,
    recipename text,
    directions text,
    author text,
    url text
);

CREATE TABLE cookbooks(
    cbid serial primary key,
    description text
);

CREATE TABLE users(
    userid  serial primary key,
    email text NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    bio text,
    datejoined timestamp,
    UNIQUE(username)
);

CREATE TABLE ingredients(
    ingid serial primary key,
    shortname text NOT NULL
);

CREATE TABLE categories(
    name text primary key
);

CREATE TABLE pantries(
    panid serial primary key,
    location text,
    userid integer references users(userid)
);

CREATE TABLE shoppinglists(
    listid serial primary key,
    active boolean,
    name text,
    userid integer references users(userid)
);


CREATE TABLE recipescontain(
    recid integer references recipes(recid),
    quantity text,
    ingid integer references ingredients(ingid),
    optional boolean,
    prep text,
    primary key(recid,ingid)
);

CREATE TABLE shoplistcontain(
    listid integer references shoppinglists(listid),
    quantity text,
    ingid integer references ingredients(ingid),
    primary key(listid,ingid)
);

CREATE TABLE pantriescontain(
    panid integer references pantries(panid),
    quantity text,
    ingid integer references ingredients(ingid),
    primary key(panid,ingid)
);

CREATE TABLE recipecategories(
    recid integer references recipes(recid),
    name text references categories(name),
    primary key(recid,name)
);

CREATE TABLE cookbookcontents(
    cbid integer references cookbooks(cbid),
    recid integer references recipes(recid),
    primary key(cbid,recid)
);

CREATE TABLE cookbookowners(
    cbid integer references cookbooks(cbid),
    userid integer references users(userid),
    primary key(cbid,userid)
);

CREATE TABLE reciperatings(
    recid integer references recipes(recid),
    userid integer references users(userid),
    rating integer,
    CHECK(rating>0),
    CHECK(rating<6),
    primary key(recid,userid)
);
