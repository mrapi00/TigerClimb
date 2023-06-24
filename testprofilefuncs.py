# ----------------------------------------------------------------------
# testprofilefuncs.py
# ----------------------------------------------------------------------
from unittest import TestCase, main
import profile_funcs as pf
from route_funcs import Session
from database_defs import Profiles

reg_name = 'test_reg'
admin_name = 'test_admin'
fake_name = 'not a real name not a real name'


class ProfileTestCase(TestCase):
    def setUp(self):
        print('profile test')

    def get_info(name):
        with Session() as session, session.begin():
            q = (session.query(Profiles).filter(Profiles.netid == reg_name).with_entities(Profiles.netid, Profiles.is_admin).all())

        return q

    def test_add_admin(self):
        pf.add_user(admin_name, True)

        q = self.get_info(admin_name)

        self.assertEqual(len(q), 1, 'incorrect number of users with name %s' % admin_name)
        self.assertTrue(q[0][1], 'user is admin')

    def test_add_existing_admin(self):
        pf.add_user(admin_name, False)
        pf.add_user(admin_name, True)

        q = self.get_info(admin_name)

        self.assertEqual(len(q), 1, 'incorrect number of users with name %s' % admin_name)
        self.assertTrue(q[0][1], 'user is admin')

    def test_add_user(self):
        pf.add_user(reg_name, False)

        q = self.get_info(reg_name)

        self.assertEqual(len(q), 1, 'incorrect number of users with name %s' % reg_name)
        self.assertFalse(q[0][1], 'user is admin')

    def test_add_existing_user(self):
        pf.add_user(reg_name, True)
        pf.add_user(reg_name, False)

        q = self.get_info(reg_name)

        self.assertEqual(len(q), 1, 'incorrect number of users with name %s' % reg_name)
        self.assertFalse(q[0][1], 'user is admin')

    def test_spam_add(self):
        for _ in range(1000):
            pf.add_user(reg_name, False)

        q = self.get_info(reg_name)

        self.assertEqual(len(q), 1, 'incorrect number of users with name %s' % reg_name)

    def test_remove_user(self):
        with self.subTest(name=reg_name):
            pf.remove_user(reg_name)

            q = self.get_info(reg_name)
            self.assertEqual(len(q), 0, 'user still exists')

        with self.subTest(name=admin_name):
            pf.remove_user(admin_name)

            q = self.get_info(reg_name)
            self.assertEqual(len(q), 0, 'user still exists')

        with self.subTest(name=fake_name):
            pf.remove_user(fake_name)

    def test_is_admin(self):
        with self.subTest(name=reg_name):
            is_admin = pf.is_admin(reg_name)

            self.assertFalse(is_admin, 'user is not admin')

        with self.subTest(name=admin_name):
            is_admin = pf.is_admin(admin_name)

            self.assertTrue(is_admin, 'user is admin')

        with self.subTest(name=fake_name):
            is_admin = pf.is_admin(fake_name)

            self.assertFalse(is_admin, 'no such user = not an admin')

    def test_user_exists(self):
        with self.subTest(name=reg_name):
            user_exists = pf.user_exists(reg_name)
            self.assertTrue(user_exists, 'user exists')

        with self.subTest(name=admin_name):
            user_exists = pf.user_exists(admin_name)
            self.assertTrue(user_exists, 'user exists')

        with self.subTest(name=fake_name):
            user_exists = pf.user_exists(fake_name)
            self.assertFalse(user_exists, 'user does not exist')

class UserExists(ProfileTestCase):
    print() # for users that do and do not exists

class UpdateAdminStatus(ProfileTestCase):
    print() # for users that are and are not admins

class ListAllUsers(ProfileTestCase):
    print() # check if the right users are in there

class AllParams(ProfileTestCase):
    print() # not sure

class AddFavorite(ProfileTestCase):
    print()

class RemoveFavorite(ProfileTestCase):
    print()

if __name__ == '__main__':
    main()