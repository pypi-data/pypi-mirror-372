# -*- coding: utf-8 -*-
from nmdc_api_utilities.data_object_search import DataObjectSearch
import logging

logging.basicConfig(level=logging.DEBUG)
from dotenv import load_dotenv
import os

load_dotenv()
ENV = os.getenv("ENV")


def test_get_do_by_study():
    """
    Test the get_data_objects_for_studies method.
    """
    do_search = DataObjectSearch(env=ENV)

    study_id = "nmdc:sty-11-aygzgv51"
    results = do_search.get_data_objects_for_studies(study_id)
    logging.debug(f"Results: {results}")
    assert results
    assert len(results) > 0
    assert "data_objects" in results[0]
