from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph


def generar_factura_pdf(pedido):
    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f'Factura pedido #{pedido.pk}',
    )
    estilos = getSampleStyleSheet()
    estilo_derecha = ParagraphStyle('derecha', parent=estilos['Normal'], alignment=TA_RIGHT)
    contenido = [
        Paragraph('<b>Beija-Flor Cosmetic</b>', estilos['Title']),
        Paragraph('Factura de venta', estilos['Heading2']),
        Spacer(1, 8 * mm),
        Paragraph(f'<b>Pedido:</b> #{pedido.pk}', estilos['Normal']),
        Paragraph(f'<b>Fecha:</b> {pedido.creado_en:%d/%m/%Y %H:%M}', estilos['Normal']),
        Spacer(1, 5 * mm),
        Paragraph(f'<b>Cliente:</b> {pedido.nombre_cliente}', estilos['Normal']),
        Paragraph(f'<b>Correo:</b> {pedido.email_cliente}', estilos['Normal']),
        Paragraph(f'<b>Dirección:</b> {pedido.direccion_entrega or "No informada"}', estilos['Normal']),
		Paragraph(f'<b>Observaciones:</b> {pedido.observaciones or "Ninguna"}', estilos['Normal']),
        Spacer(1, 8 * mm),
    ]

    filas = [['Producto', 'Variedad', 'Cantidad', 'Precio', 'Subtotal']]
    for item in pedido.items.select_related('variacion__producto').all():
        filas.append([
            item.variacion.producto.nombre,
            item.variacion.variedad,
            str(item.cantidad),
            f'R$ {item.precio_unitario:.2f}',
            f'R$ {item.subtotal:.2f}',
        ])
    filas.append(['', '', '', 'Total', f'R$ {pedido.total:.2f}'])
    tabla = Table(filas, colWidths=[52 * mm, 38 * mm, 20 * mm, 28 * mm, 30 * mm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#173b35')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -2), 0.35, colors.HexColor('#d7ddd9')),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#edf2ef')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    contenido.extend([tabla, Spacer(1, 10 * mm), Paragraph('Gracias por su compra.', estilo_derecha)])
    documento.build(contenido)
    return buffer.getvalue()
