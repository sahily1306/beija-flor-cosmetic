from django.contrib import admin
from .models import (
    AsientoContable,
    Cuenta,
    ItemPedido,
    MovimientoContable,
    Pedido,
    Producto,
    VariacionProducto,
    Grupo
)

@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'activa')
    list_filter = ('tipo', 'activa')
    search_fields = ('codigo', 'nombre')


class VariacionInline(admin.TabularInline):
    model = VariacionProducto
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'activo', 'grupo')  # 👈 aquí incluimos grupo
    list_filter = ('activo', 'categoria', 'grupo')
    search_fields = ('nombre', 'descripcion')
    inlines = (VariacionInline,)


@admin.register(VariacionProducto)
class VariacionProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'producto', 'variedad', 'precio', 'costo', 'stock', 'activa')
    list_filter = ('activa', 'producto')
    search_fields = ('sku', 'producto__nombre', 'variedad')


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    readonly_fields = ('precio_unitario', 'costo_unitario')
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'email_cliente', 'estado', 'total', 'creado_en')
    list_filter = ('estado', 'creado_en')
    search_fields = ('nombre_cliente', 'email_cliente')
    inlines = (ItemPedidoInline,)


@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'fecha', 'concepto')
    readonly_fields = ('pedido', 'fecha', 'concepto')


@admin.register(MovimientoContable)
class MovimientoContableAdmin(admin.ModelAdmin):
    list_display = ('asiento', 'cuenta', 'debito', 'credito')
    list_filter = ('cuenta',)


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

