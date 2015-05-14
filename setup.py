from setuptools import setup, find_packages
import sys, os

version = '0.9.1-alpha'

setup(
    name='ckanext-tess',
    version=version,
    description="CKAN extension for TeSS",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.tess'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        # Add plugins here, e.g.
        # myplugin=ckanext.tess.plugin:PluginClass
        tess=ckanext.tess.plugin:TeSSPlugin
        tess_controller=ckanext.tess.plugin:TeSSController
        node=ckanext.tess.node:NodePlugin
        node_controller=ckanext.tess.node:NodeController
        admin=ckanext.tess.admin:AdminPlugin
        admin_controller=ckanext.tess.admin:AdminController
        organization=ckanext.tess.organization:OrganizationPlugin
        workflow=ckanext.tess.workflow:WorkflowPlugin
        workflow_controller=ckanext.tess.workflow:WorkflowController
        package=ckanext.tess.package:PackagePlugin
    ''',
)
