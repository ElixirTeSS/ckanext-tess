__author__ = 'milo'

from ckan.tests import assert_equal, assert_in, assert_not_in, CreateTestData
import ckan.model as model

from ckanext.tess import node


class TestNodesUnit(object):

    @classmethod
    def setup_class(self):
        CreateTestData.create()
        model.Session.remove()

    @classmethod
    def teardown_class(self):
        model.Session.remove()
        model.repo.rebuild_db()
        model.Session.remove()

    def test_create_node(self):
        model.repo.new_revision()
        node = model.Group(name=u'node1', title=u'Test Node', type=u'node', description=u'This is a test node')
        model.Session.add(node)
        model.repo.commit_and_remove()
        n = model.Group.by_name(u'node1')
        assert n.title == u'Test Node'
        assert n.description == u'This is a test node'
        assert n.packages() == []
        assert n.type == u'node'

    def test_assert_false(self):
        assert_equal(False,False)

    def test_assert_fail(self):
        #assert_equal(True,False)
        pass # Tests blow up if a test fails :(

class TestMaterials(object):
    @classmethod
    def setup_class(self):
        CreateTestData.create()
        self.name = u'A Training Material'
        self.notes = 'This is really really exciting, honest.'
        materials = model.Session.query(model.Package).filter_by(name=self.name).all()
        for m in materials:
            m.purge()
        model.Session.commit()
        rev = model.repo.new_revision()
        self.mat1 = model.Package(name=self.name)
        model.Session.add(self.mat1)
        self.mat1.notes = self.notes
        self.mat1.license_id = u'odc-by'
        model.Session.commit()
        model.Session.remove()

    @classmethod
    def teardown_class(self):
        mat1 = model.Session.query(model.Package).filter_by(name=self.name).one()
        mat1.purge()
        model.Session.commit()
        model.repo.rebuild_db()
        model.Session.remove()

    def test_create_material(self):
        material = model.Package.by_name(self.name)
        assert material.name == self.name
        assert material.notes == self.notes
        assert material.license.id == u'odc-by'
        assert material.license.title == u'Open Data Commons Attribution License', material.license.title



