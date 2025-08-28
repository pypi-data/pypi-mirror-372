from copy import deepcopy
from pathlib import Path

import yaml

from gsv.logger import get_logger
from gsv.requests.utils import _get_shortname_dict


def get_derived_variables_db(derived_variables_definitions):
    default_derived_variables_def = Path(__file__).parent / "derived_variables.yaml"

    if derived_variables_definitions is None:
        return default_derived_variables_def

    return Path(derived_variables_definitions)


def norm(*args):
    """
    Take a list xarray DataArrays as arguments and return
    the Euclidean norm of them
    """
    return sum([da**2 for da in args])**0.5

def get_action_fn(action):
    ACTIONS = {
        "norm": norm
    }
    if action in ACTIONS:
        return ACTIONS[action]
    else:
        raise ValueError(f"Action {action} not recognized.")

def get_derived_variables_components(request, logger=None, derived_variables_definitions=None):
    if logger is None:
        logger = get_logger(__name__, "INFO")

    request = deepcopy(request)
    processed_params = []
    derived_variables_def = get_derived_variables_db(derived_variables_definitions)

    with open(derived_variables_def, 'r') as f:
        computed_variables = yaml.safe_load(f)
    
    for param in request['param']:
        if param in computed_variables:
            components = computed_variables[param]["components"]
            logger.debug(
                f"Variable {param} is a derived variable."
                f"Substituing FDB request by its components: {components}."
            )
            processed_params.extend(computed_variables[param]["components"])
        else:
            processed_params.append(param)
    
    request['param'] = list(set(processed_params))
    logger.debug(f"Params requested to FDB: {request['param']}")
    return request


def _get_new_da(ds, var_data, logger=None):
    if logger is None:
        logger = get_logger(__name__, "INFO")

    components_id = var_data['components']
    components_da =[ds[da_name] for da_name in ds if str(ds[da_name].attrs.get("GRIB_paramId")) in components_id]
    action_fn = get_action_fn(var_data['action'])
    new_da = action_fn(*components_da)

    # Inherit non-GRIB attributes from first componenet
    new_da.attrs = {k: v for k,v in components_da[0].attrs.items() if "GRIB" not in k}

    # Overwrite variable defining attributes
    new_da.attrs = {**new_da.attrs, **var_data['attrs']}

    # Set array name from short_name
    new_da.name = var_data['attrs']["short_name"]

    # Report on derived variable
    logger.debug(f"Derived variable {new_da.name} from: {components_id}.")

    return new_da
    

def compute_derived_variables(request, ds, definitions=None, logger=None, derived_variables_definitions=None):
    if logger is None:
        logger = get_logger(__name__, "INFO")

    derived_variables_def = get_derived_variables_db(derived_variables_definitions)

    with open(derived_variables_def, 'r') as f:
        computed_variables = yaml.safe_load(f)

    for param in request['param']:
        if param in computed_variables:
            var_data = computed_variables[param]
            da = _get_new_da(ds, var_data, logger)
            ds[da.name] = da
    
    # Drop components not in original request
    shortname2grib = _get_shortname_dict(definitions)
    for da_name in ds:
        param_id = shortname2grib[da_name]
        if param_id not in request['param']:
            ds = ds.drop_vars(da_name)

    return ds