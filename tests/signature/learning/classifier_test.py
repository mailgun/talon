from __future__ import absolute_import
from unittest.mock import patch, MagicMock
import os
import numpy as np # For creating a dummy array

from talon.signature.learning import classifier as c


@patch('talon.signature.learning.classifier.genfromtxt')
@patch('talon.signature.learning.classifier.joblib.dump')
def test_serialize(mock_joblib_dump, mock_genfromtxt):
    classifier_obj = MagicMock()
    filename = MagicMock()
    # Provide a dummy return value for genfromtxt: a 2D array with at least one row and N columns for features + 1 for label
    mock_genfromtxt.return_value = np.array([[1, 2, 3, 0]]) # e.g., 3 features, 1 label
    
    c.train(classifier_obj, "dummy_train_data.txt", filename)
    assert mock_joblib_dump.called
    mock_joblib_dump.assert_called_once_with(classifier_obj, filename)


@patch('talon.signature.learning.classifier.joblib.load')
@patch('talon.signature.learning.classifier.load_compat')
def test_deserialize_direct_joblib_load(mock_load_compat, mock_joblib_load):
    filename = MagicMock()
    mock_joblib_load.return_value = "ClassifierLoadedByJoblib"

    deserialized_classifier = c.load(filename, "dummy_train_data.txt")

    mock_joblib_load.assert_called_once_with(filename)
    assert deserialized_classifier == "ClassifierLoadedByJoblib"
    assert not mock_load_compat.called


@patch('talon.signature.learning.classifier.joblib.load')
@patch('talon.signature.learning.classifier.load_compat')
def test_deserialize_via_load_compat(mock_load_compat, mock_joblib_load):
    filename = "some_classifier_file.pkl"
    mock_joblib_load.side_effect = Exception("Failed to unpickle with joblib directly")
    mock_load_compat.return_value = "ClassifierLoadedByCompat"

    deserialized_classifier = c.load(filename, "dummy_train_data.txt")

    mock_joblib_load.assert_called_once_with(filename)
    mock_load_compat.assert_called_once_with(filename)
    assert deserialized_classifier == "ClassifierLoadedByCompat"


@patch('os.getcwd') 
@patch('os.chdir')
@patch('talon.signature.learning.classifier.open', new_callable=MagicMock)
@patch('pickle.load')
@patch('talon.signature.learning.classifier.joblib.dump')
@patch('talon.signature.learning.classifier.joblib.load')
@patch('tempfile.NamedTemporaryFile')
@patch('os.remove')
@patch('os.path.dirname')
@patch('os.path.basename')
def test_load_compat_logic(
    mock_os_path_basename,
    mock_os_path_dirname,
    mock_os_remove,
    mock_tempfile_ntf,
    mock_joblib_load_in_compat,
    mock_joblib_dump_in_compat,
    mock_pickle_load,
    mock_open,
    mock_os_chdir,
    mock_os_getcwd,
):
    saved_classifier_filename = "/path/to/data/classifier.pkl"
    mock_os_getcwd.return_value = "/original/cwd"
    mock_os_path_dirname.return_value = "/path/to/data"
    mock_os_path_basename.return_value = "classifier.pkl"
    
    mock_file_object = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file_object

    mock_pickle_load.return_value = "UnpickledLatin1Classifier"
    
    mock_temp_file_object = MagicMock()
    mock_temp_file_object.name = "/path/to/data/temp_classifier.joblib"
    mock_tempfile_ntf.return_value.__enter__.return_value = mock_temp_file_object

    mock_joblib_load_in_compat.return_value = "LoadedByJoblibFromCompatPath"

    result = c.load_compat(saved_classifier_filename)

    mock_os_getcwd.assert_called_once()
    mock_os_path_dirname.assert_called_once_with(saved_classifier_filename)
    mock_os_chdir.assert_any_call("/path/to/data")
    mock_open.assert_called_once_with("classifier.pkl", "rb")
    mock_pickle_load.assert_called_once_with(mock_open.return_value, encoding="latin1")
    mock_open.return_value.close.assert_called_once()
    
    mock_joblib_dump_in_compat.assert_any_call("UnpickledLatin1Classifier", "classifier.pkl")
    mock_joblib_load_in_compat.assert_called_once_with("classifier.pkl")
    
    assert not mock_tempfile_ntf.called
    assert not mock_os_remove.called

    mock_os_chdir.assert_any_call("/original/cwd")
    assert result == "LoadedByJoblibFromCompatPath"