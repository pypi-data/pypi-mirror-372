import pytest
from unittest.mock import patch, MagicMock

from geobox.model3d import Model
from geobox.user import User
from geobox.exception import ApiRequestError


def test_init(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    assert model.uuid == mock_model_data['uuid']
    assert model.data == mock_model_data
    assert model.endpoint == f'3dmodels/{mock_model_data["uuid"]}/'


def test_model_repr(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    assert repr(model) == f"Model(uuid={model.uuid}, name={model.name})"


def test_model_getattr(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    assert model.name == mock_model_data['name']
    assert model.description == mock_model_data['description']
    
    with pytest.raises(AttributeError):
        _ = model.nonexistent_attribute


@patch('geobox.model3d.urljoin')
@patch('geobox.model3d.urlencode')
def test_get_models(mock_urlencode, mock_urljoin, api, mock_model_data):
    mock_response = [
        mock_model_data,
        mock_model_data
    ]
    api.get.return_value = mock_response
    mock_urlencode.return_value = 'f=json'
    mock_urljoin.return_value = 'https://api.geobox.ir/v1/3dmodels/?f=json'

    models = Model.get_models(api)
    assert len(models) == 2
    assert models[0].name == mock_model_data['name']
    assert models[0].data == mock_model_data
    assert models[1].name == mock_model_data['name']

    api.get.assert_called_once_with(f"{Model.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False")

    # Test getting models with custom parameters
    api.reset_mock()
    api.get.return_value = {'count': 2}
    count = Model.get_models(
        api,
        q="name like 'test'",
        search="test",
        search_fields="name,description",
        order_by="name A",
        return_count=True,
        skip=0,
        limit=10,
        user_id=1,
        shared=False
    )
    assert count == 2
    api.get.assert_called_once_with(f"{Model.BASE_ENDPOINT}?f=json&q=name+like+%27test%27&search=test&search_fields=name%2Cdescription&order_by=name+A&return_count=True&skip=0&limit=10&user_id=1&shared=False")


@patch('geobox.model3d.urljoin')
@patch('geobox.model3d.urlencode')
def test_get_model(mock_urlencode, mock_urljoin, api, mock_model_data):
    api.get.return_value = mock_model_data
    mock_urlencode.return_value = 'f=json'

    mock_urljoin.return_value = f"3dmodels/{mock_model_data['uuid']}/?f=json"
    model = Model.get_model(api, mock_model_data['uuid'])
    assert model.uuid == mock_model_data['uuid']
    assert model.data == mock_model_data
    api.get.assert_called_once_with(f"3dmodels/{mock_model_data['uuid']}/?f=json")


@patch('geobox.model3d.urljoin')
@patch('geobox.model3d.urlencode')
def test_get_model_by_name(mock_urlencode, mock_urljoin, api, mock_model_data):
    api.get.return_value = [mock_model_data]
    mock_urlencode.return_value = 'f=json'

    mock_urljoin.return_value = f"{Model.BASE_ENDPOINT}?f=json"
    model = Model.get_model_by_name(api, name=mock_model_data['name'])
    assert model.uuid == mock_model_data['uuid']
    assert model.data == mock_model_data
    api.get.assert_called_once_with(f"{Model.BASE_ENDPOINT}?f=json&q=name+%3D+%27Treemodel%27&return_count=False&skip=0&limit=10&shared=False")
    # not found
    model = Model.get_model_by_name(api, name='not_found')
    assert model == None


def test_update(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    updated_data = {
        'name': 'Updated Name',
        'description': 'Updated Description',
        'settings': {
            'model_settings': {
                'scale': 2.0,
                'rotation': [45, 0, 0],
                'location': [1, 1, 1]
            }
        },
        'thumbnail': 'https://example.com/new-thumbnail.jpg'
    }
    api.put.return_value = updated_data

    response = model.update(
        name='Updated Name',
        description='Updated Description',
        settings=updated_data['settings'],
        thumbnail='https://example.com/new-thumbnail.jpg'
    )
    assert response == updated_data
    assert model.name == 'Updated Name'
    assert model.description == 'Updated Description'
    api.put.assert_called_once_with(model.endpoint, updated_data)


def test_delete(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    endpoint = model.endpoint
    model.delete()
    assert model.uuid is None
    assert model.endpoint is None
    api.delete.assert_called_once_with(endpoint)


import os
import pytest
from unittest.mock import MagicMock, patch
from geobox.file import File


def test_get_save_path_variants(api, mock_model_data, tmp_path):
    """Test _get_save_path edge cases."""
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)

    # Case: no save_path -> returns cwd
    result = model._get_save_path()
    assert result == os.getcwd()

    # Case: save_path ends with '/' -> returns unchanged
    path = str(tmp_path) + "/"
    assert model._get_save_path(save_path=path) == path

    # Case: save_path does NOT end with '/' -> raises ValueError
    path_invalid = str(tmp_path)
    with pytest.raises(ValueError, match="save_path must end with a '/'"):
        model._get_save_path(save_path=path_invalid)


def test_create_progress_bar_import_error(api, mock_model_data):
    """Test _create_progress_bar when tqdm is missing."""
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    model.size = 1234

    import builtins
    original_import = builtins.__import__

    def mocked_import(name, *args, **kwargs):
        if name == "tqdm.auto":
            raise ImportError("No module named 'tqdm'")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mocked_import):
        with patch("geobox.api.logger") as mock_logger:
            pbar = model._create_progress_bar()
            assert pbar is None
            mock_logger.warning.assert_called_once()


def test_download_with_obj(api, mock_model_data, tmp_path):
    """Test download() when self.data['obj'] exists."""
    # Make mock data have 'obj'
    mock_model_data['obj'] = "object-id"
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    model.name = "test_model"
    model.endpoint = "models"

    # Mock api.get_model() to return a model with a normal download
    downloaded_model = MagicMock()
    downloaded_model.api = api
    downloaded_model.name = model.name
    downloaded_model.endpoint = model.endpoint
    downloaded_model.data = {}
    downloaded_model._get_save_path = lambda sp: str(tmp_path) + "/"
    downloaded_model._create_progress_bar = lambda: MagicMock()

    api.get_model.return_value = downloaded_model

    # Mock API response
    mock_response = MagicMock()
    mock_response.__enter__.return_value.iter_content.return_value = [b"chunk"]
    mock_response.__enter__.return_value.status_code = 200
    mock_response.__exit__.return_value = None

    with patch.object(api.session, "get", return_value=mock_response), \
         patch("builtins.open", MagicMock()), \
         patch("os.makedirs", return_value=None), \
         patch("os.remove", return_value=None), \
         patch("zipfile.ZipFile", MagicMock()):
        zip_path = model.download()
        assert zip_path.endswith(".zip")


def test_download_non_200(api, mock_model_data, tmp_path):
    """Test download() raises ApiRequestError on bad status code."""
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    model.name = "test_model"
    model.endpoint = "models"

    mock_response = MagicMock()
    mock_response.__enter__.return_value.status_code = 404
    mock_response.__enter__.return_value.iter_content.return_value = []
    mock_response.__exit__.return_value = None

    with patch.object(api.session, "get", return_value=mock_response), \
         patch("os.makedirs", return_value=None):
        from geobox.api import ApiRequestError
        with pytest.raises(ApiRequestError, match="Failed to get model content: 404"):
            model.download(save_path=str(tmp_path)+"/")


def test_download_missing_uuid(api, mock_model_data):
    """Raise ValueError if UUID is missing."""
    model = Model(api, uuid=None, data=mock_model_data)  # uuid is None
    model.name = "test_model"
    model.endpoint = "models"

    from geobox.api import ApiRequestError

    with pytest.raises(ValueError, match="Model UUID is required to download content"):
        model.download()


def test_create_progress_bar_normal(api, mock_model_data):
    """Test _create_progress_bar returns tqdm instance when tqdm is available."""
    from tqdm.auto import tqdm

    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    model.size = 1024  # required for total=int(self.size)

    pbar = model._create_progress_bar()
    assert isinstance(pbar, tqdm)
    assert pbar.total == 1024


# def test_download_method_simple(api, mock_model_data, tmp_path):
#     """Test File.download() method without manually setting headers."""
#     model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
#     model.name = "test_model"  # ensure a name for filenames
#     model.endpoint = "models"

#     # Mock API response
#     mock_response = MagicMock()
#     mock_response.__enter__.return_value.iter_content.return_value = [b"chunk1", b"chunk2"]
#     mock_response.__enter__.return_value.status_code = 200
#     mock_response.__exit__.return_value = None

#     # Patch all filesystem and network operations
#     with patch.object(api.session, "get", return_value=mock_response), \
#          patch("builtins.open", new_callable=MagicMock), \
#          patch("os.makedirs", return_value=None), \
#          patch("os.remove", return_value=None), \
#          patch("zipfile.ZipFile") as mock_zip, \
#          patch.object(model, "_create_progress_bar", return_value=MagicMock()) as mock_pbar:

#         # Save to custom tmp_path
#         save_dir = str(tmp_path) + "/"
#         zip_path = model.download(save_path=save_dir)

#         # Assertions
#         assert zip_path.endswith(".zip")
#         assert os.path.commonpath([zip_path, save_dir]) == os.path.normpath(save_dir)
#         assert os.path.basename(zip_path) == "test_model.zip"
#         mock_zip.assert_called_once()  # ensure zipfile was called
#         mock_pbar.return_value.update.assert_called()  # ensure progress bar updated

#     # Test that ValueError is raised if uuid is missing
#     model.uuid = None
#     with pytest.raises(ValueError, match="Model UUID is required to download content"):
#         model.download(save_path=save_dir)
        

def test_thumbnail(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    assert model.thumbnail == f"{api.base_url}{model.endpoint}thumbnail.png"


def test_share(api, mock_model_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        model.share(users=users)
        api.post.assert_called_once_with(
            f'{model.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )

def test_unshare(api, mock_model_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        model.unshare(users=users)
        api.post.assert_called_once_with(
            f'{model.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )

def test_get_shared_users(api, mock_model_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
        result = model.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{model.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'
