#!/usr/bin/env python
# coding=utf8

from sqlalchemy import create_engine, Column, Integer, String, Sequence, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.util import classproperty
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class ACLSubject(Base):
	__tablename__ = 'acl_subjects'
	id = Column(Integer, primary_key = True)

class ACLVerb(Base):
	__tablename__ = 'acl_verbs'
	id = Column(Integer, primary_key = True)
	name = Column(String, unique = True)

class ACLObject(Base):
	__tablename__ = 'acl_objects'
	id = Column(Integer, primary_key = True)

class ACLSubjectRef(object):
	@classproperty
	def _acl_subject_id(cls):
		return Column(Integer, ForeignKey(ACLSubject.id))

	@classproperty
	def _acl_subject(cls):
		return relationship(ACLSubject)

	def init_acl(self):
		if None == self._acl_subject:
			self._acl_subject = ACLSubject()

class ACLObjectRef(object):
	@classproperty
	def _acl_object_id(cls):
		return Column(Integer, ForeignKey(ACLObject.id))

	@classproperty
	def _acl_object(cls):
		return relationship(ACLObject)

	def init_acl(self):
		if None == self._acl_object:
			self._acl_object = ACLObject()

class ACLRule(Base):
	__tablename__ = 'acl_rules'
	id = Column(Integer, primary_key = True)

	subj_id = Column(Integer, ForeignKey(ACLSubject.id))
	verb_id = Column(Integer, ForeignKey(ACLVerb.id), nullable = True)
	obj_id = Column(Integer, ForeignKey(ACLObject.id))

	subj = relationship(ACLSubject)
	verb = relationship(ACLVerb)
	obj = relationship(ACLObject)

	value = Column(Boolean)

	def __init__(self, subj_ref, verb, obj_ref, value):
		assert(hasattr(subj_ref, '_acl_subject'))
		assert(hasattr(obj_ref, '_acl_object'))

		# create subject/object if necessary
		subj_ref.init_acl()
		obj_ref.init_acl()

		self.subj = subj_ref._acl_subject
		self.verb = verb
		self.obj = obj_ref._acl_object
		self.value = value

# example
class Person(Base, ACLSubjectRef):
	__tablename__ = 'persons'
	id = Column(Integer, primary_key = True)

class Groups(Base, ACLSubjectRef):
	__tablename__ = 'groups'
	gid = Column(Integer, primary_key = True)

class Room(Base, ACLObjectRef):
	__tablename__ = 'rooms'
	id = Column(Integer, primary_key = True)

if '__main__' == __name__:
	engine = create_engine('sqlite:///test.db', echo = 'debug')
	Base.metadata.create_all(bind = engine)

	Session = sessionmaker(bind = engine)
	s = Session()

	alice = Person()
	bob = Person()
	office = Room()
	storage = Room()

	s.add(alice)
	s.add(bob)
	s.add(office)
	s.add(storage)

	s.add(ACLRule(alice, None, office, True))

	s.commit()
