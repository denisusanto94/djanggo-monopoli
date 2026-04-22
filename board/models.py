from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class Permission(models.Model):
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'permission'

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100)
    permissions = models.ManyToManyField(Permission, through='RoleHasPermission')

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.name

class RoleHasPermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'roles_has_permission'
        unique_together = ('role', 'permission')

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email harus diisi')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False) # Already in PermissionsMixin but can be explicit
    roles = models.ManyToManyField(Role, through='RoleHasUser')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

class RoleHasUser(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'roles_has_user'
        unique_together = ('role', 'user')

class Board(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'board'

    def __str__(self):
        return self.name

class Tile(models.Model):
    TILE_TYPES = (
        ('GO', 'Go'),
        ('PROPERTY', 'Property'),
        ('RAILROAD', 'Railroad'),
        ('UTILITY', 'Utility'),
        ('TAX', 'Tax'),
        ('CHANCE', 'Chance'),
        ('COMMUNITY_CHEST', 'Community Chest'),
        ('JAIL', 'Jail'),
        ('FREE_PARKING', 'Free Parking'),
        ('GO_TO_JAIL', 'Go To Jail'),
    )
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tiles')
    name = models.CharField(max_length=100)
    position = models.IntegerField() # 0 to 39
    tile_type = models.CharField(max_length=20, choices=TILE_TYPES)
    group_color = models.CharField(max_length=20, blank=True, null=True) # hex or name
    price = models.IntegerField(default=0)
    rent_base = models.IntegerField(default=0)
    house_price = models.IntegerField(default=0)
    hotel_price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='tiles/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tiles'
        ordering = ['position']
        unique_together = ('board', 'position')

    def __str__(self):
        return f"{self.name} ({self.position})"

class Menu(models.Model):
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=255)
    icon = models.CharField(max_length=100, blank=True, null=True)
    order = models.IntegerField(default=0)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    class Meta:
        db_table = 'menu'

class Card(models.Model):
    CARD_TYPES = (
        ('CHANCE', 'Chance'),
        ('COMMUNITY_CHEST', 'Community Chest'),
    )
    name = models.CharField(max_length=100)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    description = models.TextField()
    action_type = models.CharField(max_length=50, blank=True, null=True)
    value = models.IntegerField(default=0)

    class Meta:
        db_table = 'card'

class Character(models.Model):
    SHAPE_CHOICES = (
        ('square', 'Kotak'),
        ('triangle', 'Segitiga'),
        ('circle', 'Bulat'),
        ('custom', 'Custom'),
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES, default='circle')
    image = models.ImageField(upload_to='characters/', blank=True, null=True)
    color = models.CharField(max_length=20, default='#6366f1')
    model_3d = models.FileField(upload_to='characters/3d/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'characters'

    def __str__(self):
        return self.name

class AbilityCard(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    power_level = models.IntegerField(default=1)
    cooldown = models.IntegerField(default=0) # turns
    image = models.ImageField(upload_to='abilities/', blank=True, null=True)

    class Meta:
        db_table = 'ability_card'

    def __str__(self):
        return self.name

class Dice(models.Model):
    name = models.CharField(max_length=50)
    sides = models.IntegerField(default=6)

    class Meta:
        db_table = 'dice'
