#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM

__all__ = ["NonNullColumn"]


class NonNullColumn(Column):
    """SQLAlchemy column class with NOT NULL constraint by default

    This class inherits sqlalchemy.Column, but has a NOT NULL constraint by
    default.
    It also implements functions needed to generate the
    Database_Description_Document.
    """

    inherit_cache = True

    def __init__(
        self, *args, nullable=False, descr="", comment="", unique=False, **kwargs
    ):
        """
        Note that the :param comment: is not the same as the parameter 'comment'
        of sqlalchemy.Column.
        """

        self.descr = descr
        self.doc_comment = comment
        self.priority = None

        if "type_" in kwargs and kwargs["type_"]:
            self.sql_type = kwargs["type_"]
        else:
            self.sql_type = list(args).pop(0)

        if self.sql_type.__class__ == ENUM:
            self.sql_type = "ENUM"

        try:
            if kwargs["primary_key"]:
                self.priority = "PK"
        except KeyError:
            if nullable:
                self.priority = "N"
            else:
                self.priority = "NN"

        if self.priority == "PK":
            self.descr = "Primary key"

        if unique:
            self.doc_comment = f"Must be unique. {self.doc_comment}"

        # if column is a foreign key, generate the corresponding description
        try:
            fk = list(args).pop(1)
            if fk.__class__ == ForeignKey:
                if isinstance(fk._colspec, str):
                    self.descr = f"FK reference to {fk._colspec}"
                else:
                    self.descr = f"FK reference to {fk._colspec.class_.__tablename__}.{fk._colspec.key}"

        except IndexError:
            pass

        super(NonNullColumn, self).__init__(
            *args, **kwargs, nullable=nullable, unique=unique
        )

    def __repr__(self):
        infos = {
            "name": f"{self.key}",
            "sql_type": f"{self.sql_type}",
            "description": f"{self.descr}",
            "priority": f"{self.priority}",
            "comment": f"{self.doc_comment}",
        }

        return json.dumps(infos, indent=4)

    def infos(self):
        return {
            "name": f"{self.key}",
            "sql_type": f"{self.sql_type}",
            "description": f"{self.descr}",
            "priority": f"{self.priority}",
            "comment": f"{self.doc_comment}",
        }
