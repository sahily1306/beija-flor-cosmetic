from django.contrib import admin
from .models import (
	AsientoContable,
	Cuenta,
	GrupoProducto,
	ImagenProducto,
	ItemPedido,
	MovimientoContable,
	Pagamento,
	Pedido,
	Producto,
	VariacionProducto,
)


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
	list_display = ('codigo', 'nombre', 'tipo', 'activa')
	list_filter = ('tipo', 'activa')
	search_fields = ('codigo', 'nombre')


@admin.register(GrupoProducto)
class GrupoProductoAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'activo')
	list_filter = ('activo',)
	search_fields = ('nombre',)


class VariacionInline(admin.TabularInline):
	model = VariacionProducto
	extra = 1


class ImagenProductoInline(admin.TabularInline):
	model = ImagenProducto
	extra = 2


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'grupo', 'activo')
	list_filter = ('activo', 'grupo')
	search_fields = ('nombre', 'descripcion')
	inlines = (ImagenProductoInline, VariacionInline)


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
	list_display = ('id', 'nombre_cliente', 'email_cliente', 'estado', 'total', 'transportadora', 'codigo_rastreio', 'creado_en')
	list_filter = ('estado', 'creado_en')
	search_fields = ('nombre_cliente', 'email_cliente', 'codigo_rastreio')
	inlines = (ItemPedidoInline,)


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
	list_display = ('pedido', 'metodo', 'status', 'valor', 'transacao', 'criado_en')
	list_filter = ('metodo', 'status', 'criado_en')
	search_fields = ('transacao', 'pedido__nombre_cliente', 'pedido__email_cliente')


@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
	list_display = ('id', 'pedido', 'fecha', 'concepto')
	readonly_fields = ('pedido', 'fecha', 'concepto')


@admin.register(MovimientoContable)
class MovimientoContableAdmin(admin.ModelAdmin):
	list_display = ('asiento', 'cuenta', 'debito', 'credito')
	list_filter = ('cuenta',)
