# LazyPy
Lazily evaluation of python object properties through the use of a dependencies system to detect changes

Example:
~~~
  class Foo:
      def __init__(self, bar):
          self._bar = bar

      @lazyproperty()
      def bar(self):
          return self._bar

      @bar.setter
      def bar(self, bar):
          print("Setting bar")
          self._bar = bar

      @lazyproperty("self.bar")
      def sqr_bar(self):
          print("Calculating square")
          return self.bar.value**2

  foo = Foo(5)
  print(f"Getting square value twice. Should calculate square only once")
  print(f"value = {foo.bar.value}")
  print(f"sqr_value = {foo.sqr_bar.value}")
  print(f"Setting value. Should recalculate square")
  foo.bar = 4
  print(f"sqr_value = {foo.sqr_bar.value}")

  class Worker:
      def __init__(self, salary):
          self._salary = salary
          self.family = RequirableList()

      @lazyproperty()
      def salary(self):
          return self._salary

      @salary.setter
      def salary(self, value):
          self._salary = value

      @lazyproperty("(member.salary for member in self.family)", "(self.family,)")
      def total_income(self):
          return self.salary.value + sum(member.salary.value for member in self.family)

  father = Worker(10)
  mother = Worker(12)
  sons = [Worker(i+1) for i in range(5)]
  father.family.extend(sons + [mother])

  print(f"Total income: {father.total_income.value}")
  sons[3].salary = sons[3].salary.value + 3
  print(f"Total income: {father.total_income.value}")
  father.family.pop(4)  # ah, the horror...
  print(f"Total income: {father.total_income.value}")

  #output:
  #Total income: 37
  #Total income: 40
  #Total income: 35
~~~
