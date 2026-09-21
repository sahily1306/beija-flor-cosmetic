from decimal import Decimal

from django.db import models


class Cuenta(models.Model):
	class Tipo(models.TextChoices):
		ACTIVO = 'ACTIVO', 'Activo'
		PASIVO = 'PASIVO', 'Pasivo'
		PATRIMONIO = 'PATRIMONIO', 'Patrimonio'
		INGRESO = 'INGRESO', 'Ingreso'
		GASTO = 'GASTO', 'Gasto'

	codigo = models.CharField(max_length=20, unique=True)
	nombre = models.CharField(max_length=100)
	tipo = models.CharField(max_length=20, choices=Tipo.choices)
	activa = models.BooleanField(default=True)

	class Meta:
		ordering = ['codigo']
		verbose_name = 'cuenta'
		verbose_name_plural = 'cuentas'

	def __str__(self):
		return f'{self.codigo} - {self.nombre}'


class Producto(models.Model):
	nombre = models.CharField(max_length=150)
	descripcion = models.TextField(blank=True)
	categoria = models.CharField(max_length=80, blank=True)
	activo = models.BooleanField(default=True)
	imagen = models.FileField(upload_to='productos/', blank=True)
	creado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['nombre']
		verbose_name = 'producto'
		verbose_name_plural = 'productos'

	def __str__(self):
		return self.nombre


class VariacionProducto(models.Model):
	producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='variaciones')
	variedad = models.CharField(max_length=120, help_text='Ejemplo: Negro / Talla M')
	sku = models.CharField(max_length=40, unique=True)
	precio = models.DecimalField(max_digits=12, decimal_places=2)
	costo = models.DecimalField(max_digits=12, decimal_places=2)
	stock = models.PositiveIntegerField(default=0)
	activa = models.BooleanField(default=True)

	class Meta:
		ordering = ['producto__nombre', 'variedad']
		verbose_name = 'variedad de producto'
		verbose_name_plural = 'variedades de productos'

	def __str__(self):
		return f'{self.producto} - {self.variedad}'


class Pedido(models.Model):
	class Estado(models.TextChoices):
		CONFIRMADO = 'CONFIRMADO', 'Confirmado'

	nombre_cliente = models.CharField(max_length=120)
	email_cliente = models.EmailField()
	estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.CONFIRMADO)
	total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
	creado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-creado_en']
		verbose_name = 'pedido'
		verbose_name_plural = 'pedidos'

	def __str__(self):
		return f'Pedido #{self.pk} - {self.nombre_cliente}'


class ItemPedido(models.Model):
	pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
	variacion = models.ForeignKey(VariacionProducto, on_delete=models.PROTECT)
	cantidad = models.PositiveIntegerField()
	precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
	costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)

	@property
	def subtotal(self):
		return self.precio_unitario * self.cantidad

	@property
	def costo_total(self):
		return self.costo_unitario * self.cantidad


class AsientoContable(models.Model):
	pedido = models.OneToOneField(Pedido, on_delete=models.PROTECT, related_name='asiento')
	fecha = models.DateTimeField(auto_now_add=True)
	concepto = models.CharField(max_length=200)

	class Meta:
		verbose_name = 'asiento contable'
		verbose_name_plural = 'asientos contables'

	def __str__(self):
		return f'Asiento del pedido #{self.pedido_id}'


class MovimientoContable(models.Model):
	asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name='movimientos')
	cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT)
	debito = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
	credito = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

	class Meta:
		verbose_name = 'movimiento contable'
		verbose_name_plural = 'movimientos contables'

	def __str__(self):
		return f'{self.cuenta} - {self.asiento}'
