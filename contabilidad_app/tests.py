from decimal import Decimal

from django.db.models import Sum
from django.core import mail
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse

from .models import (
	AsientoContable,
	GrupoProducto,
	MovimientoContable,
	Pedido,
	Producto,
	VariacionProducto,
)


class ConfirmarCompraContabilidadTests(TestCase):
	def test_comprar_ahora_separa_el_producto_de_la_sacola(self):
		grupo = GrupoProducto.objects.create(nombre='Compra inmediata')
		producto = Producto.objects.create(nombre='Producto inmediato', grupo=grupo)
		variacion = VariacionProducto.objects.create(
			producto=producto,
			variedad='Unica',
			sku='AHORA-001',
			precio=Decimal('30.00'),
			costo=Decimal('12.00'),
			stock=2,
		)
		session = self.client.session
		session['cart'] = {'producto-que-ya-estaba': 2}
		session.save()

		response = self.client.get(f'/carrito/comprar-ahora/{variacion.pk}/')

		self.assertRedirects(response, '/carrito/')
		session = self.client.session
		self.assertEqual(session['cart'], {'producto-que-ya-estaba': 2})
		self.assertEqual(session['buy_now_cart'], {str(variacion.pk): 1})

	def test_agregar_al_carrito_conserva_la_pagina_origen(self):
		grupo = GrupoProducto.objects.create(nombre='Retorno')
		producto = Producto.objects.create(nombre='Producto retorno', grupo=grupo)
		variacion = VariacionProducto.objects.create(
			producto=producto,
			variedad='Unica',
			sku='RETORNO-001',
			precio=Decimal('25.00'),
			costo=Decimal('10.00'),
			stock=2,
		)

		response = self.client.get(
			f'/carrito/agregar/{variacion.pk}/?next=/producto/{producto.pk}/',
		)

		self.assertRedirects(response, f'/producto/{producto.pk}/')

	@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
	def test_confirmar_compra_crea_asiento_balanceado(self):
		grupo = GrupoProducto.objects.create(nombre='Pruebas')
		producto = Producto.objects.create(nombre='Producto de prueba', grupo=grupo)
		variacion = VariacionProducto.objects.create(
			producto=producto,
			variedad='Unica',
			sku='PRUEBA-001',
			precio=Decimal('100.00'),
			costo=Decimal('60.00'),
			stock=5,
		)
		session = self.client.session
		session['cart'] = {str(variacion.pk): 2}
		session.save()
		usuario = self._crear_administrador()

		response = self.client.post('/carrito/confirmar/', {
			'nombre_cliente': 'Cliente de prueba',
			'email_cliente': 'cliente@example.com',
			'observaciones': 'Embalaje para regalo y entregar por la tarde.',
			'metodo_pagamento': 'PIX',
		})

		self.assertEqual(response.status_code, 200)
		pedido = Pedido.objects.get()
		self.assertEqual(pedido.observaciones, 'Embalaje para regalo y entregar por la tarde.')
		asiento = AsientoContable.objects.get(pedido=pedido)
		movimientos = MovimientoContable.objects.filter(asiento=asiento)
		self.assertEqual(movimientos.count(), 4)
		self.assertEqual(
			movimientos.aggregate(total=Sum('debito'))['total'],
			Decimal('320.00'),
		)
		self.assertEqual(
			movimientos.aggregate(total=Sum('credito'))['total'],
			Decimal('320.00'),
		)
		self.assertEqual(VariacionProducto.objects.get(pk=variacion.pk).stock, 3)
		self.assertEqual(len(mail.outbox), 1)
		self.assertIn('cliente@example.com', mail.outbox[0].to)
		self.assertIn(usuario.email, mail.outbox[0].to)
		self.assertEqual(mail.outbox[0].attachments[0][2], 'application/pdf')

		self.client.force_login(usuario)
		factura = self.client.get(reverse('admin:contabilidad_app_pedido_factura_pdf', args=[pedido.pk]))
		self.assertEqual(factura.status_code, 200)
		self.assertEqual(factura['Content-Type'], 'application/pdf')

	def _crear_administrador(self):
		from django.contrib.auth import get_user_model

		return get_user_model().objects.create_superuser(
			username='admin-prueba',
			email='admin@example.com',
			password='password-segura-prueba',
		)
