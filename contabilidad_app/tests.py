from decimal import Decimal

from django.db.models import Sum
from django.test import TestCase
from django.urls import reverse

from .models import AsientoContable, MovimientoContable, Pedido, Producto, VariacionProducto


class TiendaTests(TestCase):
	def test_tienda_carga(self):
		response = self.client.get(reverse('tienda'))

		self.assertEqual(response.status_code, 200)

	def test_agregar_producto_al_carrito(self):
		producto = Producto.objects.create(nombre='Producto de prueba')
		variacion = VariacionProducto.objects.create(
			producto=producto,
			variedad='Unica',
			sku='CARRITO-001',
			precio=Decimal('25.00'),
			costo=Decimal('10.00'),
			stock=2,
		)

		response = self.client.get(reverse('agregar_al_carrito', args=[variacion.pk]))

		self.assertRedirects(response, reverse('tienda'))
		self.assertEqual(self.client.session['cart'], {str(variacion.pk): 1})

	def test_confirmar_compra_crea_asiento_balanceado(self):
		producto = Producto.objects.create(nombre='Producto de prueba')
		variacion = VariacionProducto.objects.create(
			producto=producto,
			variedad='Unica',
			sku='VENTA-001',
			precio=Decimal('100.00'),
			costo=Decimal('60.00'),
			stock=5,
		)
		session = self.client.session
		session['cart'] = {str(variacion.pk): 2}
		session.save()

		response = self.client.post(reverse('confirmar_compra'), {
			'nombre_cliente': 'Cliente de prueba',
			'email_cliente': 'cliente@example.com',
		})

		self.assertEqual(response.status_code, 200)
		pedido = Pedido.objects.get()
		self.assertEqual(pedido.total, Decimal('200.00'))
		movimientos = MovimientoContable.objects.filter(asiento__pedido=pedido)
		self.assertEqual(movimientos.count(), 4)
		self.assertEqual(
			movimientos.aggregate(total=Sum('debito'))['total'],
			Decimal('320.00'),
		)
		self.assertEqual(
			movimientos.aggregate(total=Sum('credito'))['total'],
			Decimal('320.00'),
		)
		self.assertEqual(AsientoContable.objects.filter(pedido=pedido).count(), 1)
		self.assertEqual(VariacionProducto.objects.get(pk=variacion.pk).stock, 3)
