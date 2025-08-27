from typing import Dict, List, Optional, Optional, Union, TYPE_CHECKING
from urllib.parse import urljoin, urlencode
import os
import zipfile
import sys
import requests
import mimetypes

from .base import Base
from .exception import ApiRequestError

if TYPE_CHECKING:
    from . import GeoboxClient
    from .user import User

class Model(Base):
    """
    A class representing a 3D model in Geobox.
    """
    BASE_ENDPOINT = '3dmodels/'

    def __init__(self, 
                 api: 'GeoboxClient', 
                 uuid: str, 
                 data: Optional[Dict] = {}):
        """
        Initialize a 3D Model instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The unique identifier for the model.
            data (Dict, optional): The data of the model.
        """
        super().__init__(api, uuid=uuid, data=data)
    

    @classmethod
    def get_models(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Model'], int]:
        """
        Get a list of models with optional filtering and pagination.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'".
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): whether to return total count. default is False.
            skip (int): number of models to skip. default is 0.
            limit (int): maximum number of models to return. default is 10.
            user_id (int): specific user. privileges required.
            shared (bool): Whether to return shared models. default is False.

        Returns:
            List[Model] | int: A list of Model objects or the count number.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> models = Model.get_models(api=client, 
            ...                           search="my_model",
            ...                           search_fields="name, description",
            ...                           order_by="name A",
            ...                           return_count=True,
            ...                           skip=0,
            ...                           limit=10,
            ...                           shared=False)
            or
            >>> models = client.get_models(search="my_model",
            ...                           search_fields="name, description",
            ...                           order_by="name A",
            ...                           return_count=True,
            ...                           skip=0,
            ...                           limit=10,
            ...                           shared=False)
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q'),
            'search': kwargs.get('search'),
            'search_fields': kwargs.get('search_fields'),
            'order_by': kwargs.get('order_by'),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 10),
            'user_id': kwargs.get('user_id'),
            'shared': kwargs.get('shared', False)
        }
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Model(api, item['uuid'], item))
    

    @classmethod
    def get_model(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'Model':
        """
        Get a model by its UUID.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the model to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Model: The model object.

        Raises:
            NotFoundError: If the model with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> model = client.get_model(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: Model(api, item['uuid'], item))


    @classmethod
    def get_model_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['Model', None]:
        """
        Get a model by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the model to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Model | None: returns the model if a model matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model_by_name(client, name='test')
            or
            >>> model = client.get_model_by_name(name='test')
        """
        models = cls.get_models(api, q=f"name = '{name}'", user_id=user_id)
        if models and models[0].name == name:
            return models[0]
        else:
            return None
    
    
    def update(self, **kwargs) -> Dict:
        """
        Update the model's properties.

        Keyword Args:
            name (str): The new name for the model.
            display_name (str): The new display name.
            description (str): The new description for the model.
            settings (Dict): The new settings for the model.
            thumbnail (str): The new thumbnail for the model.

        Returns:
            Dict: The updated model data.

        Raises:
            ValidationError: If the update data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> settings = {
            ...    "model_settings": {
            ...    "scale": 0,
            ...    "rotation": [
            ...        0
            ...    ],
            ...    "location": [
            ...        0
            ...    ]
            ...    },
            ...    "view_settings": {
            ...    "center": [
            ...        0
            ...    ],
            ...    "zoom": 0,
            ...    "pitch": 0,
            ...    "bearing": 0
            ...    }
            ... }
            >>> model.update(name="new_name", description="new_description", settings=settings, thumbnail="new_thumbnail")
        """
        data = {
            'name': kwargs.get('name'),
            'display_name': kwargs.get('display_name'),
            'description': kwargs.get('description'),
            'settings': kwargs.get('settings'),
            'thumbnail': kwargs.get('thumbnail')
        }
        return super()._update(self.endpoint, data)
    

    def delete(self) -> None:
        """
        Delete the model.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> model.delete()
        """
        super().delete(self.endpoint)


    def _get_save_path(self, save_path: str = None) -> str:
        """
        Get the path where the file should be saved.

        Args:
            save_path (str, optional): The path to save the file.

        Returns:
            str: The path where the file is saved.
        
        Raises:
            ValueError: If save_path does not end with a '/'.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> file_path = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
        """
        # If save_path is provided, check if it ends with a '/'
        if save_path and save_path.endswith('/'):
            return f'{save_path}'
        
        if save_path and not save_path.endswith('/'):
            raise ValueError("save_path must end with a '/'")
        
        return os.getcwd()


    def _create_progress_bar(self) -> 'tqdm':
        """Creates a progress bar for the task."""
        try:
            from tqdm.auto import tqdm
        except ImportError:
            from .api import logger
            logger.warning("[tqdm] extra is required to show the progress bar. install with: pip insatll geobox[tqdm]")
            return None

        return tqdm(unit="B", 
                        total=int(self.size), 
                        file=sys.stdout,
                        dynamic_ncols=True,
                        desc="Downloading",
                        unit_scale=True,
                        unit_divisor=1024, 
                        ascii=True
                )


    def download(self, save_path: str = None, progress_bar: bool = True) -> str:
        """
        Download the 3D model, save it as a .glb file, zip it, and return the zip file path.

        Args:
            save_path (str, optional): Directory where the file should be saved.
            progress_bar (bool, optional): Whether to show a progress bar. Default: True

        Returns:
            str: Path to the .zip file containing the .glb model.

        Raises:
            ApiRequestError: If the API request fails.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> model = client.get_models()[0]
            >>> model.get_content()
        """
        if not self.uuid:
            raise ValueError("Model UUID is required to download content")

        if self.data.get('obj'):
            model = self.api.get_model(self.obj)
        else:
            model = self

        save_path = model._get_save_path(save_path)
        os.makedirs(save_path, exist_ok=True)

        endpoint = urljoin(model.api.base_url, f"{model.endpoint}/content/")
        with model.api.session.get(endpoint, stream=True) as response:
            if response.status_code != 200:
                raise ApiRequestError(f"Failed to get model content: {response.status_code}")

            glb_filename = f"{model.name}.glb"
            glb_path = os.path.join(save_path, glb_filename)

            with open(glb_path, "wb") as f:
                pbar = model._create_progress_bar() if progress_bar else None
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    if pbar:
                        pbar.update(len(chunk))
                        pbar.refresh()
                if pbar:
                    pbar.close()

        zip_filename = f"{model.name}.zip"
        zip_path = os.path.join(save_path, zip_filename)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(glb_path, arcname=os.path.basename(glb_path))

        os.remove(glb_path)

        return os.path.abspath(zip_path)


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail URL of the model.

        Returns:
            str: The thumbnail of the model.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> model.thumbnail
        """
        return super().thumbnail()
    

    def share(self, users: List['User']) -> None:
        """
        Shares the model with specified users.

        Args:
            users (List[users]): The list of user objects to share the model with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> model.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the model with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the model with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> model.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the model is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> model.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)
