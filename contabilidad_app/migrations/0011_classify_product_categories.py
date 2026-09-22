from django.db import migrations


CATEGORIES = {
    'Vela do Amor': 'Velas aromáticas',
    'Kit do Amor': 'Kits de presentes',
    'Vela Aquatica': 'Velas aromáticas',
    'Sabonete Artesanal de Arroz e Rosa Mosqueta': 'Sabonetes artesanais',
    'Feliz Natal': 'Velas aromáticas',
    'Mini velas': 'Velas aromáticas',
    'Sabonete Camomila': 'Sabonetes artesanais',
    'Sabonete Carvão': 'Sabonetes artesanais',
    'Vela Halloween': 'Velas aromáticas',
    'Body Splash Jazmin': 'Body splash',
    'Body Splash Baunilha': 'Body splash',
}


def classify_products(apps, schema_editor):
    Producto = apps.get_model('contabilidad_app', 'Producto')
    for nombre, categoria in CATEGORIES.items():
        Producto.objects.filter(nombre=nombre, categoria='').update(categoria=categoria)


def unclassify_products(apps, schema_editor):
    Producto = apps.get_model('contabilidad_app', 'Producto')
    Producto.objects.filter(categoria__in=CATEGORIES.values()).update(categoria='')


class Migration(migrations.Migration):
    dependencies = [
        ('contabilidad_app', '0010_remove_producto_grupo_remove_imagenproducto_producto_and_more'),
    ]

    operations = [
        migrations.RunPython(classify_products, unclassify_products),
    ]
