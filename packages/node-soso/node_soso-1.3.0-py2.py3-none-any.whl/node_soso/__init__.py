#  node_soso/__init__.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
XML enhancements to make a few things easier.
"""
import re
import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element

__version__ = "1.3.0"


def dump_file(filename):
	with open(filename) as fob:
		dump_from_string(fob.read())

def dump_from_string(data):
	xml = et.fromstring(data)
	dump(xml, 0)

def dump(el, depth=0):
	s = '  ' * depth + el.tag
	if len(el.attrib):
		s += ' (' + ', '.join( '%s:%s' % (k,v) for k,v in el.attrib.items() ) + ')'
	if el.text is not None and len(el.text.rstrip()):
		s += ': "' + el.text.rstrip() + '"'
	print(s)
	for c in el:
		dump(c, depth+1)

def concise_xml(el):
	spc_between = re.compile('>\s+<')
	spc_ending = re.compile('\s+\/>')
	return spc_ending.sub('/>', spc_between.sub('><', et.tostring(el).decode())).strip()


class SmartNode(Element):

	def __init__(self, element, parent = None):
		self.element = element
		self._parent = parent

	@property
	def parent(self):
		return self._parent

	def child(self, node_name, create = True):
		element = self.element.find(node_name)
		return et.SubElement(self.element, node_name) \
			if create and element is None else element

	def find(self, path):
		return self.element.find(path)

	def findall(self, path):
		return self.element.findall(path)

	def element_text(self, path, default = None):
		el = self.find(path)
		return default if el is None else el.text

	def attribute_value(self, name, default = None):
		return self.element.attrib[name] if name in self.element.attrib else default

	@classmethod
	def from_string(cls, string, parent = None):
		return cls(et.fromstring(string), parent)

	@classmethod
	def from_element(cls, element, parent = None):
		return cls(element, parent)

	@classmethod
	def from_elements(cls, elements, parent = None):
		return [ cls(element, parent) for element in elements ]

	def concise_xml(self):
		return concise_xml(self.element)

	def dump(self):
		if self.element is None:
			print("ELEMENT IS NONE")
		else:
			dump(self.element)


class SmartTree:

	def __init__(self, filename):
		self.filename = filename
		self.tree = et.parse(filename)
		self.element = self.tree.getroot()

	def find(self, path):
		return self.tree.find(path)

	def findall(self, path):
		return self.tree.findall(path)

	def dump(self):
		dump(self.element)

	def print(self):
		print(et.tostring(self.element).decode())



#  end node_soso/__init__.py
