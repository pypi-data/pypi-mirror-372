# -*- coding: utf-8 -*-
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound


def one(session, model, **filters):
    return session.query(model).filter_by(**filters).one()


def create(session, model, **kwargs):
    obj = model(**kwargs)
    session.add(obj)
    session.commit()
    return obj


def get_or_create(
    session, model, create_method="", create_method_kwargs=None, **kwargs
):
    """
    Simply get an object if already present in the database or create it in the
    other case. See
    http://skien.cc/blog/2014/01/15/sqlalchemy-and-race-conditions-implementing/
    and
    http://skien.cc/blog/2014/02/06/sqlalchemy-and-race-conditions-follow-up/
    for better details on why this function as been upgraded to the provided
    example. Better handling of weird cases in the situation of multiple
    processes using the database at the same time.
    """
    try:
        return one(session, model, **kwargs)
    except NoResultFound:
        kwargs.update(create_method_kwargs or {})
        created = getattr(model, create_method, model)(**kwargs)
        try:
            session.add(created)
            session.commit()
            return created
        except IntegrityError:
            session.rollback()
            return one(session, model, **kwargs)
