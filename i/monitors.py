

from i.models import ProductCategory, ComputerSubCategory, Special_Features, Monitors, CustomUser

def populate_monitors():
    monitors_data = [
        {
            'name': 'Monitor 8',
            'brand': 'DELL',  # Replace with the desired brand
            'aspect_ratio': '16:9',  # Replace with the aspect ratio
            'max_display_resolution': '1920x1080',  # Replace with the max display resolution
            'screen_size': '24"',  # Replace with the screen size
            'monitor_type': 'CARE_MONITOR',  # Replace with the monitor type
            'refresh_rate': '144 Hz',  # Replace with the refresh rate
            'mounting_type': 'DESK_MOUNT',  # Replace with the mounting type
            'item_dimensions': '20x10x5 inches',  # Replace with item dimensions
            'item_weight': 3000,  # Replace with item weight
            'voltage': 220,  # Replace with voltage
            'color': 'Black',  # Replace with the color
            'hdmi_port': 2.0,  # Replace with HDMI port value
            'built_speakers': 'yes',  # Replace with built-in speakers value
            'price': 299.99,  # Replace with the price
            'quantity': 10,  # Replace with quantity
            'Product_Category': ProductCategory.objects.get_or_create(pk=1)[0],
            'Computer_SubCategory': ComputerSubCategory.objects.get_or_create(pk=5)[0],
            'user': CustomUser.objects.get_or_create(pk=2)[0],
            'monitor_id': 8,
            
        }, {

            'name': 'Monitor 9',
            'brand': 'Acer',  # Replace with the desired brand
            'aspect_ratio': '16:9',  # Replace with the aspect ratio
            'max_display_resolution': '1920x1080',  # Replace with the max display resolution
            'screen_size': '24"',  # Replace with the screen size
            'monitor_type': 'CARE_MONITOR',  # Replace with the monitor type
            'refresh_rate': '144 Hz',  # Replace with the refresh rate
            'mounting_type': 'DESK_MOUNT',  # Replace with the mounting type
            'item_dimensions': '20x10x5 inches',  # Replace with item dimensions
            'item_weight': 3000,  # Replace with item weight
            'voltage': 220,  # Replace with voltage
            'color': 'Black',  # Replace with the color
            'hdmi_port': 2.0,  # Replace with HDMI port value
            'built_speakers': 'yes',  # Replace with built-in speakers value
            'price': 99.99,  # Replace with the price
            'quantity': 10,  # Replace with quantity
            'Product_Category': ProductCategory.objects.get_or_create(pk=1)[0],
            'Computer_SubCategory': ComputerSubCategory.objects.get_or_create(pk=5)[0],
            'user': CustomUser.objects.get_or_create(pk=2)[0],
            'monitor_id': 9,
           
            },
    ]
    
    special_features = [
    Special_Features.objects.get_or_create(name='frameless')[0],
    Special_Features.objects.get_or_create(name='eye_care')[0]
]
    
    for feature in special_features:
         feature.save()


    for data in monitors_data:
            monitor_instance = Monitors(**data)
            monitor_instance.save()
            
            for feature in special_features:
                 monitor_instance.special_features.add(feature)

                 