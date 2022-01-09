from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase

class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        '''Test waiting for DB when it is ready to accept connections'''
        # Try retrieve DB connection - if OperationalError -- DB available
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        '''Test waiting for DB'''
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Raise OperationalError on first 5 attempts, but not on the 6th
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
