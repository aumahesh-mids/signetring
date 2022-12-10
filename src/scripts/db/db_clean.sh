#!/bin/zsh

psql postgresql://admin:admin@localhost:5432/ta << EOF
  delete from ta_auth;
  delete from ta_user;
  delete from ta_sourceapp;
  delete from ta_digitalobject;
  delete from ta_challenge;
  delete from ta_publishedobject;
EOF
