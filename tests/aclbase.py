#!/usr/bin/env python
# coding=utf8

import unittest
from model import *

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

class ACLBasicTest(unittest.TestCase):
	def setUp(self):
		from sqlalchemy import create_engine
		from sqlalchemy.orm import sessionmaker

		#import uuid
		#self.dbfilename = '%s.db' % uuid.uuid4()
		#self.engine = create_engine('sqlite:///%s' % self.dbfilename, echo = 'debug')
		self.engine = create_engine('sqlite:///:memory:', echo = 'debug')
		Base.metadata.drop_all(bind = self.engine)
		Base.metadata.create_all(bind = self.engine)
		Session = sessionmaker(bind = self.engine)
		self.s = Session()

		self.alice = Person()
		self.bob = Person()
		self.office = Room()
		self.storage = Room()

		self.s.add(self.alice)
		self.s.add(self.bob)
		self.s.add(self.office)
		self.s.add(self.storage)

		self.s.commit()

	def test_acl_verb_retrieval(self):
		v = ACLVerb('some_verb')
		self.s.add(v)
		self.s.commit()

		self.assertEqual(v, ACLVerb.get_by_name(self.s, 'some_verb'))

	def test_acl_verb_autocreation(self):
		v = ACLVerb.get_by_name(self.s, 'my_verb')
		self.s.commit()
		self.assertEqual(v, ACLVerb.get_by_name(self.s, 'my_verb'))

	def test_acl_verb_string_conversion(self):
		vstr = 'a_verb'
		verb = ACLVerb(vstr)
		self.s.add(verb)

		self.assertEqual(verb, ACLVerb.get(self.s, verb))
		self.assertEqual(verb, ACLVerb.get(self.s, vstr))

	def test_simple_rule(self):
		enter = ACLVerb('enter')
		exit = ACLVerb('exit')
		self.alice.permit('enter')
		self.s.commit()

		self.assertTrue(self.alice.may('enter'))
		self.assertFalse(self.alice.may('exit'))

		self.alice.permit('exit')
		self.assertTrue(self.alice.may('exit'))

	def test_object_rules_adding_permissions(self):
		enter = ACLVerb('enter')

		self.assertFalse(self.alice.may('enter'))
		self.assertFalse(self.alice.may('enter', self.office))
		self.assertFalse(self.alice.may('enter', self.storage))

		self.alice.permit('enter', self.office)

		self.assertFalse(self.alice.may('enter'))
		self.assertFalse(self.alice.may('enter', self.storage))
		self.assertTrue(self.alice.may('enter', self.office))

		self.s.commit()
