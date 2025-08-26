import math
from itertools import chain
from copy import deepcopy

from django.contrib.admin import AdminSite
from django.conf import settings

REST_KEY = "__rest__"


def _build_order_config():
    order_config = {}
    order_counter = 0
    for order_item in settings.ADMIN_REORDER:
        app_name = order_item['app']
        app_order_config = order_config.get(app_name, None)
        if not app_order_config:
            app_order_config = {
                'order': order_counter,
                'config': [],
                'is_virtual': False,  # Track if this is a virtual app group
            }
            order_counter += 1
        app_order_config['config'].append(order_item)
        order_config[app_name] = app_order_config

    return order_config


def _build_all_models_dict(app_list):
    """Build a dictionary of all models indexed by app_label.model_name"""
    models_dict = {}
    for app in app_list:
        for model in app['models']:
            model_name = f"{app['app_label']}.{model['object_name']}"
            models_dict[model_name] = model
    return models_dict


def _process_model_config(model_config, models_dict):
    """Process a single model configuration, handling both strings and dicts"""
    if isinstance(model_config, dict):
        # Handle custom model labels: {'model': 'auth.User', 'label': 'Staff'}
        if 'model' in model_config and 'label' in model_config:
            model_name = model_config['model']
            if model_name in models_dict:
                model = deepcopy(models_dict[model_name])
                model['name'] = model_config['label']
                return model
    else:
        # Handle simple model reference: 'auth.User' or 'sites.Site'
        model_name = str(model_config)
        if '.' not in model_name:
            # If no app prefix, we can't cross-link, so return None
            return None
        if model_name in models_dict:
            return deepcopy(models_dict[model_name])
    return None


def _order_app_subsets(app, order_config, all_models_dict):
    app_config = order_config.get(app['app_label'], None)
    if not app_config:
        return [app]

    # Extract used models from this app's configuration
    used_models = set()
    for subset in app_config['config']:
        models = subset.get('models', [])
        if isinstance(models, (list, tuple)):
            for model in models:
                if isinstance(model, dict):
                    if 'model' in model:
                        model_name = model['model']
                        # Extract just the object name for this app's models
                        if '.' in model_name:
                            app_label, obj_name = model_name.split('.', 1)
                            if app_label == app['app_label']:
                                used_models.add(obj_name)
                        else:
                            used_models.add(model_name)
                else:
                    model_str = str(model)
                    if '.' in model_str:
                        app_label, obj_name = model_str.split('.', 1)
                        if app_label == app['app_label']:
                            used_models.add(obj_name)
                    else:
                        used_models.add(model_str)

    unused_models = set(map(
        lambda model: model['object_name'],
        app['models']
    )).difference(used_models)

    app_subsets = []
    for subset_config in app_config['config']:
        app_subset = deepcopy(app)
        app_subset['name'] = subset_config.get('label', app['name'])
        models = subset_config.get('models', None)
        
        if models is not None:
            app_subset_models = []
            if isinstance(models, (list, tuple)):
                # Skip app completely if models is an empty list
                if len(models) == 0:
                    continue
                    
                for model_config in models:
                    if isinstance(model_config, dict):
                        # Handle custom model labels
                        model = _process_model_config(model_config, all_models_dict)
                        if model:
                            app_subset_models.append(model)
                    else:
                        # Handle string model references (including cross-app)
                        model_str = str(model_config)
                        if '.' in model_str:
                            # Cross-app model reference
                            model = _process_model_config(model_str, all_models_dict)
                            if model:
                                app_subset_models.append(model)
                        else:
                            # Local app model
                            model = next(filter(
                                lambda m: m['object_name'] == model_str,
                                app['models']
                            ), None)
                            if model:
                                app_subset_models.append(deepcopy(model))
                                
            elif models == REST_KEY:
                app_subset_models = [
                    deepcopy(model) for model in app['models']
                    if model['object_name'] in unused_models
                ]
                
            app_subset['models'] = app_subset_models

        app_subsets.append(app_subset)

    return app_subsets


def _get_app_order(app, order_config):
    app_name = app['app_label']
    app_config = order_config.get(app_name, None)
    return app_config['order'] if app_config else math.inf


def _create_virtual_app(app_name, app_config, all_models_dict):
    """Create a virtual app group with models from different real apps"""
    virtual_app = {
        'name': app_config['config'][0].get('label', app_name.replace('_', ' ').title()),
        'app_label': app_name,
        'app_url': f'/admin/{app_name}/',
        'has_module_perms': True,
        'models': [],
    }
    
    # Process each configuration for this virtual app
    for subset_config in app_config['config']:
        models = subset_config.get('models', [])
        if isinstance(models, (list, tuple)):
            # Skip virtual app completely if models is an empty list
            if len(models) == 0:
                return None
                
            for model_config in models:
                if isinstance(model_config, dict):
                    # Handle custom model labels
                    model = _process_model_config(model_config, all_models_dict)
                    if model:
                        virtual_app['models'].append(model)
                else:
                    # Handle string model references (must be cross-app for virtual)
                    model_str = str(model_config)
                    if '.' in model_str:
                        model = _process_model_config(model_str, all_models_dict)
                        if model:
                            virtual_app['models'].append(model)
    
    return virtual_app


def _identify_virtual_apps(order_config, app_list):
    """Identify which configured apps are virtual (don't exist in Django)"""
    real_app_labels = {app['app_label'] for app in app_list}
    
    for app_name, app_config in order_config.items():
        if app_name not in real_app_labels:
            app_config['is_virtual'] = True
    
    return order_config


def _build_new_order(app_list):
    order_config = _build_order_config()
    all_models_dict = _build_all_models_dict(app_list)
    order_config = _identify_virtual_apps(order_config, app_list)
    
    # Separate real and virtual apps
    real_apps = [app for app in app_list if not order_config.get(app['app_label'], {}).get('is_virtual', False)]
    virtual_apps = []
    
    # Create virtual apps
    for app_name, app_config in order_config.items():
        if app_config.get('is_virtual', False):
            virtual_app = _create_virtual_app(app_name, app_config, all_models_dict)
            if virtual_app and virtual_app['models']:  # Only add if it exists and has models
                virtual_apps.append(virtual_app)
    
    # Process real apps
    ordered_real_apps = sorted(
        real_apps,
        key=lambda app: _get_app_order(app, order_config),
    )
    real_app_subsets = list(map(
        lambda app: _order_app_subsets(app, order_config, all_models_dict),
        ordered_real_apps,
    ))
    
    # Combine and sort all apps (real subsets + virtual apps) by order
    all_apps = list(chain.from_iterable(real_app_subsets)) + virtual_apps
    
    # Sort by the order specified in configuration
    final_apps = sorted(all_apps, key=lambda app: _get_app_order(app, order_config))
    
    return final_apps


class ReorderingAdminSite(AdminSite):
    def get_app_list(self, request, app_label=None):
        app_list = list(self._build_app_dict(request).values())
        reordered_app_list = list(_build_new_order(app_list))
        
        # If app_label is provided (Django 5.1+), filter the list
        if app_label:
            reordered_app_list = [app for app in reordered_app_list if app["app_label"] == app_label]
            
        return reordered_app_list
