# -*- coding: utf-8 -*-
"""
This is the initial module that contains the pytest configuration fixtures
"""
import pytest
import os
from app import create_app
from app import db as _db
from app.models import Dataset, DatasetStats, Pipeline, User, AffiliationType, \
    OAuth, Role
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from config import TestingConfig
from datetime import datetime, timedelta

from flask_login import current_user, login_user, logout_user


@pytest.fixture(scope='session')
def app(request):
    """
    This is creates the mock app for testing, it uses the
    TestingConfig in Config.py
    """
    app = create_app(config_settings=TestingConfig)

    return app


@pytest.fixture(scope='session')
def db(app, request):
    """
    This is creates the test db
    """
    test_db_file = app.config['SQLALCHEMY_DATABASE_URI'].split(":///")[1]

    if os.path.exists(test_db_file):
        os.unlink(test_db_file)

    def teardown():
        _db.drop_all()
        os.unlink(test_db_file)

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """
    This creates a mock session
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection)
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        session.close()
        transaction.rollback()
        connection.close()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def test_client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='module')
def new_dataset():
    """
    Creates a new mock dataset to test
    """
    dataset = Dataset(
        dataset_id="8de99b0e-5f94-11e9-9e05-52545e9add8e",
        annex_uuid="4fd032a1-220a-404e-95ac-ccaa3f7efcb7",
        description="Human Brain phantom scans, Multiple MRI"
        " scans of a single human phantom over 11"
        " years, T1 weighted images and others on"
        " 13 scanner in 6 sites accross North America."
        " The data are available in minc format",
        owner_id=1,
        download_path="multicenter-phantom",
        raw_data_url="https://phantom-dev.loris.ca",
        name="Multicenter Single Subject Human MRI Phantom",
        modality="Imaging",
        version="1.0",
        format="minc",
        category="Phantom",
        is_private=False,

    )
    return dataset


@pytest.fixture(scope='module')
def new_dataset_stats():
    """
    Creates a new mock DatasetStats to test
    """
    dataset_stats = DatasetStats(
        dataset_id="8de99b0e-5f94-11e9-9e05-52545e9add8e",
        size=40,
        files=2712,
        sources=1,
        num_subjects=1,
        num_downloads=0,
        num_likes=0,
        num_views=0,

    )
    return dataset_stats


@pytest.fixture(scope='module')
def new_pipeline():
    """
    Creates a new mock dataset to test
    """
    pipeline = Pipeline(
        id=1,
        pipeline_id=12,
        owner_id=1,
        name='Freesurfer',
        version='1.9',
        is_private=False,
        date_created=datetime.now(),
        date_updated=datetime.now()
    )
    return pipeline


@pytest.fixture(scope='module')
def new_affiliation_type():
    """
    Creates a new mock affiliation_type to test
    """
    affiliation_type = AffiliationType(
        name="PR",
        label="Professor"
    )
    return affiliation_type


@pytest.fixture(scope='module')
def new_user(app, new_affiliation_type):
    """
    Creates a new mock user for us to test things
    """
    user = User(
        email="example@mailinator.com",
        affiliation="CONP",
        affiliation_type=new_affiliation_type,
        full_name="Example User",
        expiration=datetime.utcnow() + timedelta(days=30),
        password=app.user_manager.hash_password("ThisPassword")
    )
    return user
