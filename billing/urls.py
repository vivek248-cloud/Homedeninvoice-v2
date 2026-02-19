from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),


    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile, name='profile'),
    path('password-change/', views.admin_password_change, name='password_change'),



    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/update/<int:pk>/', views.client_update, name='client_update'),
    path('clients/delete/<int:pk>/', views.client_delete, name='client_delete'),



    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/update/<int:pk>/', views.project_update, name='project_update'),
    path('projects/delete/<int:pk>/', views.project_delete, name='project_delete'),

    path('projects/<int:pk>/', views.project_detail, name='project_detail'),





    path('floors/', views.floor_list, name='floor_list'),
    path('floors/create/', views.floor_create, name='floor_create'),
    path('floors/update/<int:pk>/', views.floor_update, name='floor_update'),
    path('floors/delete/<int:pk>/', views.floor_delete, name='floor_delete'),



    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/update/<int:pk>/', views.room_update, name='room_update'),
    path('rooms/delete/<int:pk>/', views.room_delete, name='room_delete'),




    path('fullsemi/', views.fullsemi_list, name='fullsemi_list'),
    path('fullsemi/create/', views.fullsemi_create, name='fullsemi_create'),
    path('fullsemi/update/<int:pk>/', views.fullsemi_update, name='fullsemi_update'),
    path('fullsemi/delete/<int:pk>/', views.fullsemi_delete, name='fullsemi_delete'),




    path('spends/', views.spend_list, name='spend_list'),
    path('spends/create/', views.spend_create, name='spend_create'),
    path('spends/update/<int:pk>/', views.spend_update, name='spend_update'),
    path('spends/delete/<int:pk>/', views.spend_delete, name='spend_delete'),



    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/update/<int:pk>/', views.payment_update, name='payment_update'),
    path('payments/delete/<int:pk>/', views.payment_delete, name='payment_delete'),

    path('payments/<int:pk>/invoice/', views.payment_invoice, name='payment_invoice'),
    path('invoice/<uuid:token>/', views.public_invoice, name='public_invoice'),




    path('backup/download/', views.download_backup, name='download_backup'),
    path('backup/restore/', views.restore_backup, name='restore_backup'),
    
    path('backup/history/', views.backup_history, name='backup_history'),
    path('backup/download/<str:filename>/', views.download_backup_file, name='download_backup_file'),
    path(
        "backup/delete/<str:filename>/",
        views.delete_backup_file,
        name="delete_backup_file",
    ),

    path(
        "payments/<int:pk>/save-adjustments/",
        views.save_invoice_adjustments,
        name="save_invoice_adjustments",
    ),


]
