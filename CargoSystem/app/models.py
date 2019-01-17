from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class UserQuerySet(models.query.QuerySet):
    def all(self):
        return self.filter(is_active=True)

class UserManager(BaseUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given, email, and password.
        """
        if not username:
            raise ValueError('The username can not be null')
        if not email:
            raise ValueError('The email can not be null')
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser):

    FEMALE  = _('female')
    MALE    = _('male')

    MANAGER = _('manager')
    TRANSPORTER = _('transporter')
    CUSTOMER = _('customer')

    USERTYPE_CHOICES = (
        (MANAGER, _('Manager')),
        (TRANSPORTER, _('Transporter')),
        (CUSTOMER, _('Customer'))
    )

    username 	 	 = models.CharField(_('Username'),
                                      unique=True,
                                      max_length=255,
                                      error_messages={
                                        "unique": _("The username is already exist."),
                                      })

    email 		 	 = models.EmailField(_('E-Mail Address'), max_length=255, unique=True)
    first_name	 	 = models.CharField(_('First Name'), max_length=30, blank=True)
    last_name	 	 = models.CharField(_('Last Name'), max_length=150, blank=True)
    date_joined	 	 = models.DateTimeField(_('Date Joined'), default=timezone.now)

    is_active	 	 = models.BooleanField(_('Active Status'),
                                            default=True,
                                            help_text=_(
                                                'Designates whether this user account should be considered active.'
                                                ' Set this flag to False instead of deleting accounts.'
                                            ))

    is_staff	 	 = models.BooleanField(_('Staff Status'),
                                            default=False,
                                            help_text=_(
                                                'Designates whether this user can access the admin site.'
                                            ))

    is_superuser 	 = models.BooleanField(_('Super User Status'),
                                             default=False,
                                             help_text=_(
                                                'Designates that this user has all permissions'
                                                ' without explicitly assigning them.'
                                             ))

    user_type		 = models.CharField(_('User Type'),
                                        max_length=50,
                                        choices=USERTYPE_CHOICES,
                                        default=CUSTOMER)

    tc_no = models.IntegerField(_('TC NO'),
                            unique=True,
                            null=True,
                            blank=True,
                            error_messages={
                                "unique": _("The username is already exist."),
                            })

    EMAIL_FIELD 	 = 'email'
    USERNAME_FIELD 	 = 'username'
    REQUIRED_FIELDS  = ['email']

    objects = UserManager()

    class Meta:
        verbose_name 		= _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.username

    def get_full_name(self):
        fullname = '{0} {1}'.format(self.first_name, self.last_name)
        if not fullname.strip():
            fullname = self.username
        return fullname.strip()

    def get_short_name(self):
        first_name = self.first_name
        if not first_name:
            first_name = self.username
        return first_name

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class IsikCargos(models.Model):
    to_who              = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='receiver')
    from_who            = models.CharField(max_length=255, null=False, blank=False)
    who_has_now         = models.ForeignKey('User',on_delete=models.SET_NULL, null=True, related_name='current')
    created_cargo_date  = models.DateTimeField(auto_now_add=True)
    taken_cargo_date    = models.DateField(blank=True, null=True)

    def taken(self):
        self.taken_cargo_date=timezone.now()
        self.save()