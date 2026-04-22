from django.db import migrations

def add_default_characters(apps, schema_editor):
    Character = apps.get_model('board', 'Character')
    default_characters = [
        {'name': 'Mobil Merah', 'color': '#ef4444', 'description': 'Token mobil balap warna merah cerah.'},
        {'name': 'Topi Hitam', 'color': '#1e293b', 'description': 'Token topi klasik warna hitam elegan.'},
        {'name': 'Kapal Biru', 'color': '#3b82f6', 'description': 'Token kapal laut warna biru samudra.'},
        {'name': 'Sepatu Cokelat', 'color': '#92400e', 'description': 'Token sepatu bot warna cokelat tanah.'},
        {'name': 'Anjing Putih', 'color': '#f8fafc', 'description': 'Token anjing lucu warna putih bersih.'},
        {'name': 'Dadu Emas', 'color': '#fbbf24', 'description': 'Token dadu keberuntungan warna emas.'},
    ]
    for char in default_characters:
        Character.objects.get_or_create(name=char['name'], defaults=char)

def remove_default_characters(apps, schema_editor):
    Character = apps.get_model('board', 'Character')
    names = ['Mobil Merah', 'Topi Hitam', 'Kapal Biru', 'Sepatu Cokelat', 'Anjing Putih', 'Dadu Emas']
    Character.objects.filter(name__in=names).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('board', '0003_character_color_character_model_3d'),
    ]

    operations = [
        migrations.RunPython(add_default_characters, remove_default_characters),
    ]
