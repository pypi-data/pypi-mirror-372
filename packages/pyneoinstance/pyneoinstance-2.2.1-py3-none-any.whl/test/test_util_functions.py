# -*- coding: utf-8 -*-
"""Module use to test the utility functions"""

import os
import pandas as pd
import unittest
from datetime import datetime
from .context import util
from .context import fileload

class TestUtilFunctions(unittest.TestCase):
    """Test the util function to generate file names.

        Methods
        -------
        test_get_file_name()
            Test the function that generates file names.
        test_is_reachable_url()
            Test if a url exists and is reachable.
    """

    def test_get_file_name(self):
        """Test the file name generator."""
        file_format='log'
        file_name_parts = ['neo4j','debug']
        result = util.get_file_name(
            file_format,file_name_parts)
        file_name_parts.append(datetime.today().strftime('%Y%m%d'))
        file_name_parts.append(datetime.now().strftime('%H%M%S'))
        solution ='_'.join(file_name_parts) + '.' + file_format
        self.assertEqual(solution,result)

    def test_is_reachable_url(self):
        """Test the util function that determines if a URL is reachable."""
        url_scheme = 'file'
        url_loc = os.path.abspath(os.path.dirname(__file__))
        file_name = 'movies.csv'
        url = url_scheme + '://' + url_loc + '/' + file_name
        result =  util.is_reachable_url(url)
        self.assertTrue(result)

    def test_get_colums_diff(self):
        print('Columns Diff')
        data_file_name = 'movies.csv'
        cypher_file_name = 'cypher_queries.yaml'
        file_location = os.path.abspath(os.path.dirname(__file__))
        cypher_file = os.path.join(file_location,cypher_file_name)
        query = fileload.load_yaml_file(cypher_file)['queries']['load_movie']
        columns = pd.read_csv(os.path.join(file_location,data_file_name)).columns
        result = util.get_columns_diff(query, columns)
        solution = []
        self.assertEqual(solution,result)
