from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
	AsientoContable,
	Cuenta,
	ItemPedido,
	MovimientoContable,
	Pedido,
	Producto,
	VariacionProducto,
)


def tienda(request):
	productos = Producto.objects.filter(activo=True, variaciones__activa=True).prefetch_related('variaciones').order_by('categoria', 'nombre').distinct()
	return render(request, 'contabilidad_app/tienda.html', {'productos': productos})


def atendimento_ia(request):
	return render(request, 'contabilidad_app/atendimento con ia/chat.html')


def agregar_al_carrito(request, variacion_id):
	variacion = get_object_or_404(VariacionProducto, pk=variacion_id, activa=True)
	cart = request.session.get('cart', {})
	key = str(variacion.pk)
	nueva_cantidad = int(cart.get(key, 0)) + 1
	if nueva_cantidad > variacion.stock:
		messages.error(request, 'No hay más unidades disponibles de esta variedad.')
	else:
		cart[key] = nueva_cantidad
		request.session['cart'] = cart
		messages.success(request, 'Producto agregado al carrito.')
	return redirect('tienda')


def carrito(request):
	items = _items_del_carrito(request)
	total = sum((item['subtotal'] for item in items), Decimal('0.00'))
	return render(request, 'contabilidad_app/carrito.html', {'items': items, 'total': total})


@transaction.atomic
def confirmar_compra(request):
	if request.method != 'POST':
		return redirect('carrito')

	items = _items_del_carrito(request, bloquear_stock=True)
	if not items:
		messages.error(request, 'Tu carrito está vacío.')
		return redirect('carrito')

	nombre = request.POST.get('nombre_cliente', '').strip()
	email = request.POST.get('email_cliente', '').strip()
	if not nombre or not email:
		messages.error(request, 'Completa tu nombre y correo para confirmar la compra.')
		return redirect('carrito')

	total = sum((item['subtotal'] for item in items), Decimal('0.00'))
	costo_total = sum((item['costo_total'] for item in items), Decimal('0.00'))
	for item in items:
		if item['variacion'].stock < item['cantidad']:
			messages.error(request, f'Ya no hay stock suficiente de {item["variacion"]}.')
			return redirect('carrito')

	pedido = Pedido.objects.create(nombre_cliente=nombre, email_cliente=email, total=total)
	for item in items:
		variacion = item['variacion']
		variacion.stock -= item['cantidad']
		variacion.save(update_fields=['stock'])
		ItemPedido.objects.create(
			pedido=pedido,
			variacion=variacion,
			cantidad=item['cantidad'],
			precio_unitario=variacion.precio,
			costo_unitario=variacion.costo,
		)

	asiento = AsientoContable.objects.create(
		pedido=pedido,
		concepto=f'Venta simulada del pedido #{pedido.pk}',
	)
	cuentas = _cuentas_base()
	MovimientoContable.objects.bulk_create([
		MovimientoContable(asiento=asiento, cuenta=cuentas['caja'], debito=total),
		MovimientoContable(asiento=asiento, cuenta=cuentas['ventas'], credito=total),
		MovimientoContable(asiento=asiento, cuenta=cuentas['costo'], debito=costo_total),
		MovimientoContable(asiento=asiento, cuenta=cuentas['inventario'], credito=costo_total),
	])
	request.session['cart'] = {}
	return render(request, 'contabilidad_app/compra_confirmada.html', {'pedido': pedido})


def _items_del_carrito(request, bloquear_stock=False):
	cart = request.session.get('cart', {})
	items = []
	for variacion_id, cantidad in cart.items():
		queryset = VariacionProducto.objects.select_related('producto')
		if bloquear_stock:
			queryset = queryset.select_for_update()
		variacion = queryset.filter(pk=variacion_id, activa=True).first()
		if variacion:
			cantidad = int(cantidad)
			items.append({
				'variacion': variacion,
				'cantidad': cantidad,
				'subtotal': variacion.precio * cantidad,
				'costo_total': variacion.costo * cantidad,
			})
	return items


def _cuentas_base():
	def cuenta(codigo, nombre, tipo):
		return Cuenta.objects.get_or_create(codigo=codigo, defaults={'nombre': nombre, 'tipo': tipo})[0]

	return {
		'caja': cuenta('1.1.01', 'Caixa', Cuenta.Tipo.ACTIVO),
		'inventario': cuenta('1.1.03', 'Estoque de mercadorias', Cuenta.Tipo.ACTIVO),
		'ventas': cuenta('4.1.01', 'Receita de vendas', Cuenta.Tipo.INGRESO),
		'costo': cuenta('5.1.01', 'Custo das mercadorias vendidas', Cuenta.Tipo.GASTO),
	}


def dashboard(request):
	cuentas = Cuenta.objects.all()
	context = {
		'total_cuentas': cuentas.count(),
		'cuentas_activas': cuentas.filter(activa=True).count(),
		'tipos_registrados': cuentas.values('tipo').annotate(total=Count('id')).order_by('-total', 'tipo'),
		'cuentas_recientes': cuentas[:6],
	}
	return render(request, 'contabilidad_app/dashboard.html', context)

