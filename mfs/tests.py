""" Test module

Example:
    ~$ ./server/manage.py test mfs.tests.DirTestCase.save
"""

from django.test import TestCase
from .models import Dir


class DirTestCase(TestCase):
    def setUp(self):
        # Dir.objects.create(path="dir01")
        # Dir.objects.create(path="dir02")
        # Dir.objects.create(path="rootdir/dir03")
        pass

    def set_path(self):
        """Testing of set_path() function of a Dir"""
        Dir.objects.create(path="dir01")
        Dir.objects.create(path="dir02")
        Dir.objects.create(path="rootdir/dir03")

        d01 = Dir.objects.get(relpath='dir01')
        d02 = Dir.objects.get(relpath='dir02')
        d03 = Dir.objects.get(relpath='rootdir/dir03')

        d01.set_path('parent/dir01/')
        d02.set_path('/root/parent/dir02/')

        d01.save()
        d02.save()
    
        d03.path = '/documents/files'
        d03.save()

        print("d01: {}".format(d01))
        print("d01: {}".format(d01))
        print("d03: {}".format(d03))
        
        self.assertEqual(d01.relpath, '/parent/dir01/')
        self.assertEqual(d02.relpath, '/root/parent/dir02/')
        self.assertEqual(d03.relpath, '/documents/files/')

    def truediv(self):
        """Testing of the / operator function"""
        d01 = Dir.objects.get(relpath='dir01')
        d02 = Dir.objects.get(relpath='dir02')
        d03 = Dir.objects.get(relpath='rootdir/dir03')

        d04 = d01 / d02
        y02 = d01 / 'middle/'
        y03 = d02 / 'relpather/directory/'
        y04 = d02 / '/rootdir/dir03/file/'
        y05 = d01 / d02 / d03
        y03 = y05 / d03

        print("d01: {}".format(d01))
        print("d01: {}".format(d02))
        print("d04: {}".format(d04))
        print("y02: {}".format(y02))
        print("y03: {}".format(y02))
        print("y04: {}".format(y02))
        print("y05: {}".format(y02))
    
    def save(self):
        d1 = Dir("d1")
        d2 = Dir("d1")
        
        d1.save()
        d2.save()
        
        self.assertEqual(d1.id, d2.id)

    def iadd(self):
        d = Dir('root_dir/')
        d1 = Dir('d1')
        d2 = Dir('d2')

        d.save()
        d1.save()
        d2.save()
        
        d += d1
        d += d2
        
        print(d.subdirectories.all())


