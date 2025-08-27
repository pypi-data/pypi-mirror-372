from ._config import _check_all_environment_variables_are_set

_check_all_environment_variables_are_set()


### Public Methods ###
from ._requests_utils import requests_get, requests_put, requests_delete, requests_patch, requests_post
from .get_dataset_custom_view import get_dataset_custom_view
from .get_dataset_license import get_dataset_license
from .get_dataset_metadata import get_dataset_metadata
from .get_dataset_metadata_temporal_period import get_dataset_metadata_temporal_period
from .get_dataset_title import get_dataset_title
from .get_all_dataset_ids import get_all_dataset_ids
from .get_number_of_datasets import get_number_of_datasets
from .get_template_metadata import get_template_metadata
from .get_uid_by_id import get_uid_by_id
from .set_dataset_license import set_dataset_license
from .set_dataset_metadata_temporal_coverage_end_date import set_dataset_metadata_temporal_coverage_end_date
from .set_dataset_metadata_temporal_coverage_start_date import set_dataset_metadata_temporal_coverage_start_date
from .set_dataset_metadata_temporal_period import set_dataset_metadata_temporal_period
from .set_dataset_public import set_dataset_public
from .set_template_metadata import set_template_metadata
