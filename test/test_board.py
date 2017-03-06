from django.test import TestCase
from monitor.models import Board

class BoardTest(TestCase):

    def test_defconfig(self):
        board = Board(defconfiglist='foo bar')
        self.assertEqual(['foo', 'bar'], board.defconfigs)
