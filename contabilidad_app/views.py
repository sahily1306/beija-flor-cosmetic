from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
	AsientoContable,
	Cuenta,
	ItemPedido,
	MovimientoContable,
	Pagamento,
	Pedido,
	Producto,
	GrupoProducto,
	VariacionProducto,
)


def tienda(request, grupo_id=None):
	grupos = GrupoProducto.objects.filter(activo=True)
	grupo_seleccionado = None
	productos = Producto.objects.filter(
		activo=True,
		variaciones__activa=True,
	).prefetch_related('variaciones').distinct()
	if grupo_id is not None:
		grupo_seleccionado = get_object_or_404(grupos, pk=grupo_id)
	return render(request, 'contabilidad_app/tienda.html', {
		'productos': productos,
		'grupos': grupos,
		'grupo_seleccionado': grupo_seleccionado,
	})


def detalle_producto(request, producto_id):
	producto = get_object_or_404(
		Producto.objects.prefetch_related('imagenes', 'variaciones'),
		pk=producto_id,
		activo=True,
	)
	return render(request, 'contabilidad_app/detalle_producto.html', {'producto': producto})


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


def eliminar_del_carrito(request, variacion_id):
	if request.method == 'POST':
		cart = request.session.get('cart', {})
		if str(variacion_id) in cart:
			del cart[str(variacion_id)]
			request.session['cart'] = cart
			messages.success(request, 'Producto eliminado de la sacola.')
	return redirect('carrito')


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
		messages.error(request, 'Seu carrinho está vazio.')
		return redirect('carrito')

	nombre = request.POST.get('nombre_cliente', '').strip()
	email = request.POST.get('email_cliente', '').strip()
	telefono = request.POST.get('telefono_cliente', '').strip()
	direccion = request.POST.get('direccion_entrega', '').strip()
	ciudad = request.POST.get('ciudad', '').strip()
	provincia = request.POST.get('provincia', '').strip()
	codigo_postal = request.POST.get('codigo_postal', '').strip()
	metodo_pagamento = request.POST.get('metodo_pagamento', Pagamento.Metodo.PIX)
	if not nombre or not email:
		messages.error(request, 'Preencha seu nome e e-mail para confirmar a compra.')
		return redirect('carrito')
	if metodo_pagamento not in Pagamento.Metodo.values:
		messages.error(request, 'Selecione uma forma de pagamento válida.')
		return redirect('carrito')

	total = sum((item['subtotal'] for item in items), Decimal('0.00'))
	costo_total = sum((item['costo_total'] for item in items), Decimal('0.00'))
	for item in items:
		if item['variacion'].stock < item['cantidad']:
			messages.error(request, f'Ya no hay stock suficiente de {item["variacion"]}.')
			return redirect('carrito')

	pedido = Pedido.objects.create(
		nombre_cliente=nombre,
		email_cliente=email,
		telefono_cliente=telefono,
		direccion_entrega=direccion,
		ciudad=ciudad,
		provincia=provincia,
		codigo_postal=codigo_postal,
		total=total,
	)
	Pagamento.objects.create(
		pedido=pedido,
		metodo=metodo_pagamento,
		valor=total,
		transacao=f'SIM-{pedido.pk:08d}',
	)
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


@login_required(login_url='/admin/login/')
def pedidos(request):
	if request.method == 'POST':
		pedido = get_object_or_404(Pedido, pk=request.POST.get('pedido_id'))
		estado = request.POST.get('estado', '')
		if estado in Pedido.Estado.values:
			pedido.estado = estado
			pedido.transportadora = request.POST.get('transportadora', '').strip()
			pedido.codigo_rastreio = request.POST.get('codigo_rastreio', '').strip()
			pedido.save(update_fields=['estado', 'transportadora', 'codigo_rastreio'])
			messages.success(request, f'Pedido #{pedido.pk} actualizado.')
		return redirect('pedidos')

	estado_filtro = request.GET.get('estado', '')
	lista = Pedido.objects.prefetch_related('items__variacion__producto').all()
	if estado_filtro in Pedido.Estado.values:
		lista = lista.filter(estado=estado_filtro)
	return render(request, 'contabilidad_app/pedidos.html', {
		'pedidos': lista,
		'estado_filtro': estado_filtro,
		'estados': Pedido.Estado.choices,
		'agora': timezone.now(),
	})

