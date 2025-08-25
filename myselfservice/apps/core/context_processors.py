from django.apps import apps

def navigation_context(request):
    nav_items = []
    dashboard_items = []
    
    for app_config in apps.get_app_configs():
        if hasattr(app_config, 'nav_config'):
            config = app_config.nav_config
            
            # Permission check
            if config.get('permission'):
                if not request.user.has_perm(config['permission']):
                    continue
            
            nav_item = {
                'title': config['title'],
                'icon': config['icon'],
                'url_name': config['url_name'],
                'app_name': app_config.name,
                'order': config.get('order', 999),
                'description': config.get('description', ''),
            }
            
            nav_items.append(nav_item)
            dashboard_items.append(nav_item)
    
    # Nach order sortieren
    nav_items.sort(key=lambda x: x['order'])
    dashboard_items.sort(key=lambda x: x['order'])
    
    return {
        'nav_items': nav_items,
        'dashboard_items': dashboard_items,
    }