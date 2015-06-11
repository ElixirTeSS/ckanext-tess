__author__ = 'milo'

from ckan.tests import assert_equal, assert_in, assert_not_in, CreateTestData
from ckan.tests.functional.base import FunctionalTestCase
import ckan.model as model
import ckan.lib.search as search

from ckanext.tess import node

class TestNodesFunctional(FunctionalTestCase):

    @classmethod
    def setup_class(self):
        search.clear()
        model.Session.remove()
        CreateTestData.create()

        # reduce extraneous logging
        from ckan.lib import activity_streams_session_extension
        activity_streams_session_extension.logger.level = 100

    @classmethod
    def teardown_class(self):
        model.repo.rebuild_db()

    def test_working(self):
        assert_equal(True,True)


class TestOtherStuff(FunctionalTestCase):

    def test_something(self):
        assert_equal(True,True)