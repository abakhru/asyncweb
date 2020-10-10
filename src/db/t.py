#!/usr/bin/env python


def get_user(**kwargs):
    for key, value in kwargs.items():
        print(f"session.query(users).filter(users.c.'{key}' == '{value}').all()")


get_user(email='test@amit.com')
