import logging
import unittest

from kywy.client.kawa_decorators import KawaScriptInput, KawaScriptOutput

from ..scripts.metadata_checker import MetaDataChecker


class MetaDataCheckerTest(unittest.TestCase):
    def test_do_not_throw_when_same_metadata(self):
        kawa_input = [KawaScriptInput(dataframe=None, name='measure1', type='DECIMAL')]
        kawa_output = [KawaScriptOutput(name='output1', type='TEXT')]
        repo_input = [KawaScriptInput(dataframe=None, name='measure1', type='DECIMAL')]
        repo_output = [KawaScriptOutput(name='output1', type='TEXT')]

        metadata_checker = MetaDataChecker(kawa_inputs=kawa_input,
                                            kawa_outputs=kawa_output,
                                            kawa_parameters=[],
                                            repo_inputs=repo_input,
                                            repo_outputs=repo_output,
                                            repo_parameters=[],
                                            kawa_logger=logging.getLogger())
        try:
            metadata_checker.check()
        except Exception:
            self.fail('Should not raise when meta data are the same')

    def test_throw_when_missing_input_in_kawa(self):
        kawa_input = [KawaScriptInput(dataframe=None, name='measure1', type='DECIMAL')]
        kawa_output = [KawaScriptOutput(name='output1', type='TEXT')]
        repo_input = [KawaScriptInput(dataframe=None, name='measure1', type='DECIMAL'),
                      KawaScriptInput(dataframe=None, name='measure2', type='DECIMAL')]
        repo_output = [KawaScriptOutput(name='output1', type='TEXT')]

        metadata_checker = MetaDataChecker(kawa_inputs=kawa_input,
                                            kawa_outputs=kawa_output,
                                            kawa_parameters=[],
                                            repo_inputs=repo_input,
                                            repo_outputs=repo_output,
                                            repo_parameters=[],
                                            kawa_logger=logging.getLogger())

        self.assertRaises(Exception, lambda x: metadata_checker.check())

    def test_throw_when_outputs_have_different_types(self):
        kawa_input = [KawaScriptInput(dataframe=None, name='measure1', type='DECIMAL')]
        kawa_output = [KawaScriptOutput(name='output1', type='TEXT')]
        repo_input = [KawaScriptInput(dataframe=None, name='measure1', type='DECIMAL')]
        repo_output = [KawaScriptOutput(name='output1', type='DECIMAL')]

        metadata_checker = MetaDataChecker(kawa_inputs=kawa_input,
                                            kawa_outputs=kawa_output,
                                            kawa_parameters=[],
                                            repo_inputs=repo_input,
                                            repo_outputs=repo_output,
                                            repo_parameters=[],
                                            kawa_logger=logging.getLogger())

        self.assertRaises(Exception, lambda x: metadata_checker.check())

    def test_throw_when_repo_misses_outputs(self):
        kawa_input = [KawaScriptInput(dataframe=None, name='measure1', type='DECIMAL')]
        kawa_output = [KawaScriptOutput(name='output1', type='TEXT'),
                       KawaScriptOutput(name='output2', type='TEXT')]
        repo_input = [KawaScriptInput(dataframe=None, name='measure1', type='DECIMAL')]
        repo_output = [KawaScriptOutput(name='output1', type='TEXT')]

        metadata_checker = MetaDataChecker(kawa_inputs=kawa_input,
                                            kawa_outputs=kawa_output,
                                            kawa_parameters=[],
                                            repo_inputs=repo_input,
                                            repo_outputs=repo_output,
                                            repo_parameters=[],
                                            kawa_logger=logging.getLogger())

        self.assertRaises(Exception, lambda x: metadata_checker.check())


if __name__ == '__main__':
    unittest.main()
