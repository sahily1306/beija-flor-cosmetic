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


class GrupoProducto(models.Model):
	nombre = models.CharField(max_length=80, unique=True)
	imagen = models.ImageField(upload_to='grupos/', blank=True)
	activo = models.BooleanField(default=True)

	class Meta:
		ordering = ['nombre']
		verbose_name = 'grupo de productos'
		verbose_name_plural = 'grupos de productos'

	def __str__(self):
		return self.nombre


class Producto(models.Model):
	nombre = models.CharField(max_length=150)
	descripcion = models.TextField(blank=True)
	grupo = models.ForeignKey(
		GrupoProducto,
		on_delete=models.PROTECT,
		related_name='productos',
		null=True,
		blank=True,
	)
	activo = models.BooleanField(default=True)
	imagen = models.FileField(upload_to='productos/', blank=True)
	creado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['nombre']
		verbose_name = 'producto'
		verbose_name_plural = 'productos'

	def __str__(self):
		return self.nombre


class ImagenProducto(models.Model):
	producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
	imagen = models.ImageField(upload_to='productos/')
	orden = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ['orden', 'id']
		verbose_name = 'imagen de producto'
		verbose_name_plural = 'imágenes de productos'

	def __str__(self):
		return f'Imagen de {self.producto.nombre}'


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
		SEPARANDO = 'SEPARANDO', 'Separando pedido'
		ENVIADO = 'ENVIADO', 'Enviado'
		ENTREGUE = 'ENTREGUE', 'Entregue'
		CANCELADO = 'CANCELADO', 'Cancelado'

	nombre_cliente = models.CharField(max_length=120)
	email_cliente = models.EmailField()
	telefono_cliente = models.CharField(max_length=30, blank=True)
	direccion_entrega = models.CharField(max_length=200, blank=True)
	ciudad = models.CharField(max_length=80, blank=True)
	provincia = models.CharField(max_length=80, blank=True)
	codigo_postal = models.CharField(max_length=20, blank=True)
	estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.CONFIRMADO)
	total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
	transportadora = models.CharField(max_length=100, blank=True)
	codigo_rastreio = models.CharField(max_length=100, blank=True)
	creado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-creado_en']
		verbose_name = 'pedido'
		verbose_name_plural = 'pedidos'

	def __str__(self):
		return f'Pedido #{self.pk} - {self.nombre_cliente}'


class Pagamento(models.Model):
	class Metodo(models.TextChoices):
		PIX = 'PIX', 'Pix'
		CARTAO = 'CARTAO', 'Cartão de teste'
		BOLETO = 'BOLETO', 'Boleto bancário'

	class Status(models.TextChoices):
		APROVADO = 'APROVADO', 'Aprovado'

	pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pagamento')
	metodo = models.CharField(max_length=20, choices=Metodo.choices)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.APROVADO)
	valor = models.DecimalField(max_digits=12, decimal_places=2)
	transacao = models.CharField(max_length=40, unique=True)
	criado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = 'pagamento'
		verbose_name_plural = 'pagamentos'

	def __str__(self):
		return f'Pagamento do pedido #{self.pedido_id}'


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
