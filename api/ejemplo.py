class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    auth0_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # opcional
    names = models.CharField(max_length=150, null=True, blank=True, verbose_name='Nombres')
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    image = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True, verbose_name='Imagen')

    is_active = models.BooleanField(default=True, verbose_name='Estado')
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # campos de tu modelo anterior que quieras conservar
    is_change_password = models.BooleanField(default=False)
    email_reset_token = models.TextField(null=True, blank=True)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['names']



class User(AbstractBaseUser, PermissionsMixin):
    names = models.CharField(max_length=150, null=True, blank=True, verbose_name='Nombres')
    username = models.CharField(max_length=150, unique=True, verbose_name='Username')
    # dni = models.CharField(max_length=10, unique=True, verbose_name='Número de cedula')
    image = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True, verbose_name='Imagen')
    email = models.EmailField(null=True, blank=True, verbose_name='Correo electrónico')
    is_active = models.BooleanField(default=True, verbose_name='Estado')
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_change_password = models.BooleanField(default=False)
    email_reset_token = models.TextField(null=True, blank=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
