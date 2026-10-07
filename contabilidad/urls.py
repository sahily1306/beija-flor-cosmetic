"""
URL configuration for contabilidad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from contabilidad_app import views

urlpatterns = [
    path('', views.tienda, name='tienda'),
    path('coleccion/<str:grupo_id>/', views.tienda_grupo, name='tienda_grupo'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('producto/<int:producto_id>/comprar/', views.comprar_producto_ahora, name='comprar_producto_ahora'),
    path('chat/', views.atendimento_ia, name='atendimento_ia'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:variacion_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/comprar/<int:variacion_id>/', views.comprar_ahora, name='comprar_ahora'),
    path('carrito/remover/<int:variacion_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/confirmar/', views.confirmar_compra, name='confirmar_compra'),
    path('gestion/', views.dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
