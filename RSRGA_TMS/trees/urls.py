from django.urls import path

from RSRGA_TMS.trees import views

urlpatterns = [
    path('map/', views.interactive_mapping, name='map_view'),
    path('Tree_Inventory/', views.tree_inventory, name='tree_inventory'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('tree_inventory/export_csv/', views.export_tree_inventory_csv, name='export_tree_inventory_csv'),
]