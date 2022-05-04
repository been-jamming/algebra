import math

class GroupElement:
	def __init__(self):
		self.group = None
	def __neg__(self):
		raise NotImplementedError
	def __mul__(self, x):
		raise NotImplementedError
	def __eq__(self, x):
		raise NotImplementedError

class Group:
	def __init__(self):
		self.parent = None
		self.generators = None
	def element(self, identifier):
		raise NotImplementedError
	def subgroup_normal(self, subgroup):
		raise NotImplementedError
	def subgroup_member(self, element, subgroup):
		raise NotImplementedError

class Homomorphism:
	def __init__(self):
		self.domain = None
		self.codomain = None
		self.identity = None
	def eval(self, element):
		raise NotImplementedError
	def kernel(self):
		raise NotImplementedError
	def image(self):
		raise NotImplementedError

class IntegersElement(GroupElement):
	def __init__(self, n, group):
		if type(n) is not int:
			raise TypeError("Expected integer value.")
		if type(group) is not Integers:
			raise TypeError("Expected group 'Integers'.")
		self.group = group
		self.value = n
	def __neg__(self):
		return IntegersElement(-self.value, self.group)
	def __mul__(self, x):
		if type(x) is not IntegersElement:
			raise TypeError("Expected integer element.")
		if x.group != self.group:
			raise TypeError("Group elements do not belong to same group.")
		return IntegersElement(self.value + x.value, self.group)
	def __eq__(self, x):
		if type(x) is not IntegersElement:
			raise TypeError("Expected integer element.")
		if x.group != self.group:
			raise TypeError("Group elements do not belong to same group.")
		return self.value == x.value
	def __repr__(self):
		return "IntegersElement(%d, %s)"%(self.value, str(self.group))
	def __str__(self):
		return str(self.value)

class Integers(Group):
	def __init__(self):
		self.parent = None
		self.identity = IntegersElement(0, self)
	def element(self, identifier):
		if type(identifier) is not int:
			raise TypeError("Expected integer value.")
		return IntegersElement(identifier, self)
	def subgroup_normal(self, subgroup):
		if not issubclass(type(subgroup), Group) or subgroup.parent is not self:
			raise TypeError("Expected subgroup.")
		return True
	def subgroup_member(self, element, subgroup):
		if not issubclass(type(element), GroupElement) or element.group is not self:
			raise TypeError("Expected group element.")
		if not issubclass(type(subgroup), Group) or subgroup.parent is not self:
			raise TypeError("Expected subgroup.")
		single_generator = math.gcd(*[generator.value for generator in subgroup.original_generators])
		return element.value%single_generator == 0
	def __repr__(self):
		return "Integers()"

class SubgroupElement(GroupElement):
	def __init__(self, element, subgroup):
		if not issubclass(type(element), GroupElement) or element.group != subgroup.parent:
			raise TypeError("Expected subgroup element from parent group.")
		self.group = subgroup
		self.value = element
	def __neg__(self):
		return SubgroupElement(-self.value, self.group)
	def __mul__(self, x):
		if type(x) is not SubgroupElement:
			raise TypeError("Expected subgroup element.")
		if x.group != self.group:
			raise TypeError("Group elements do not belong to same group.")
		return SubgroupElement(self.value*x.value, self.group)
	def __eq__(self, x):
		if type(x) is not SubgroupElement:
			raise TypeError("Expected subgroup element.")
		if x.group != self.group:
			raise TypeError("Group elements do not belong to same group.")
		return self.value == x.value
	def __repr__(self):
		return "SubgroupElement(%s, %s)"%(repr(self.value), repr(self.group))
	def __str__(self):
		return str(self.value)

class Subgroup(Group):
	def __init__(self, generators, parent):
		if not issubclass(type(parent), Group):
			raise TypeError("Expected group.")
		for generator in generators:
			if not issubclass(type(generator), GroupElement) or generator.group != parent:
				raise TypeError("Expected group elements.")
		self.parent = parent
		self.identity = SubgroupElement(parent.identity, self)
		self.generators = [SubgroupElement(generator, self) for generator in generators]
		self.original_generators = generators
	def element(self, identifier):
		if type(identifier) is not int:
			raise TypeError("Expected integer value.")
		return self.generators[identifier]
	def subgroup_normal(self, subgroup):
		if not issubclass(type(subgroup), Group) or subgroup.parent is not self:
			raise TypeError("Expected subgroup.")
		parent_generators = self.original_generators + [generator.value for generator in subgroup.original_generators]
		new_subgroup = Subgroup(parent_generators, self.parent)
		return self.parent.subgroup_normal(new_subgroup)
	def subgroup_member(self, element, subgroup):
		if not issubclass(type(element), GroupElement) or element.group is not self:
			raise TypeError("Expected group element.")
		if not issubclass(type(subgroup), Group) or subgroup.parent is not self:
			raise TypeError("Expected subgroup.")
		parent_generators = [generator.value for generator in subgroup.original_generators]
		new_subgroup = Subgroup(parent_generators, self.parent)
		return self.parent.subgroup_member(element.value, new_subgroup)
	def __repr__(self):
		return "Subgroup(%s, %s)"%(repr(self.original_generators), repr(self.parent))

class QuotientElement(GroupElement):
	def __init__(self, representative, quotient):
		if not issubclass(type(representative), GroupElement) or representative.group is not quotient.dividend:
			raise TypeError("Representative must be group element of quotiented group")
		self.group = quotient
		self.value = representative
	def __neg__(self):
		return QuotientElement(-self.value, self.group)
	def __mul__(self, x):
		if type(x) is not QuotientElement:
			raise TypeError("Expected quotient element.")
		if x.group != self.group:
			raise TypeError("Group elements do not belong to the same group.")
		return QuotientElement(self.value*x.value, self.group)
	def __eq__(self, x):
		if type(x) is not QuotientElement:
			raise TypeError("Expected quotient element.")
		if x.group != self.group:
			raise TypeError("Group elements do not belong to the same group.")
		return self.group.dividend.subgroup_member((self*-x).value, self.group.divisor)
	def __repr__(self):
		return "QuotientElement(%s, %s)"%(repr(self.value), repr(self.group))
	def __str__(self):
		return str(self.value)

class Quotient(Group):
	def __init__(self, dividend, divisor):
		if not issubclass(type(dividend), Group):
			raise TypeError("Expected group.")
		if not issubclass(type(divisor), Group) or divisor.parent is not dividend:
			raise TypeError("Expected normal subgroup.")
		if not dividend.subgroup_normal(divisor):
			raise TypeError("Subgroup is not normal.")
		self.parent = None
		self.dividend = dividend
		self.divisor = divisor
		self.identity = QuotientElement(self.dividend.identity, self)
	def element(self, identifier):
		return QuotientElement(self.dividend.element(identifier), self)
	def __repr__(self):
		return "Quotient(%s, %s)"%(repr(self.dividend), repr(self.divisor))
