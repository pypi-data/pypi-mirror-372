# object_startup_test.py
import datetime
import layer_cake as lc

from test_person import *

table_Person_type = lc.def_type(lc.VectorOf(lc.VectorOf(lc.UserDefined(Person))))
table_world_type = lc.def_type(lc.VectorOf(lc.VectorOf(lc.WorldTime())))

def main(self, height: int=4, width: int=4, who: Person=None, when: datetime.datetime=None):
	self.console(f'width: {width}, height: {height}')

	if height < 1 or height > 1000 or width < 1 or width > 1000:
		return lc.Faulted(f'out of bounds')

	if who:
		table = [[who] * width] * height
		return lc.cast_to(table, table_Person_type)

	if when:
		table = [[when] * width] * height
		return lc.cast_to(table, table_world_type)

	return (True, lc.Boolean())

lc.bind(main, return_type=lc.Any())

if __name__ == '__main__':
	lc.create(main)
