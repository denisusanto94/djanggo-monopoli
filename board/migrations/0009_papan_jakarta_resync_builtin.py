# Manual — sinkron nama/deskripsi & petak papan bawaan setelah tema Jakarta

from django.db import migrations


def forwards(apps, schema_editor):
    Board = apps.get_model('board', 'Board')
    Tile = apps.get_model('board', 'Tile')
    from board.default_tiles_seed import seed_tiles_for_board

    for board in Board.objects.filter(is_builtin=True):
        board.name = 'Papan Jakarta'
        board.description = (
            'Papan bawaan: 32 petak DKI Jakarta (board/tiles.py). Dapat diedit di admin; '
            'tombol Generate mengisi ulang dari definisi kode.'
        )
        board.save(update_fields=['name', 'description', 'updated_at'])
        seed_tiles_for_board(board, Tile)


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0008_board_is_builtin_classic'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
