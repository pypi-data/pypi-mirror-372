# models/base.py
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar, cast

from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from typing_extensions import Self

from adjango.managers.base import AManager, AUserManager
from adjango.utils.funcs import arelated

if TYPE_CHECKING:
    from adjango.services.base import ABaseService


class AModel(Model):
    """Base model class with enhanced functionality."""

    objects: AManager[Self] = AManager()

    class Meta:
        abstract = True

    async def arelated(self, field: str) -> Any:
        """
        Get related field value asynchronously.
        """
        return await arelated(self, field)

    @property
    def service(self) -> 'ABaseService':
        """Return service instance for this model. Must be implemented in subclasses."""
        raise NotImplementedError(f'Define service property in your model {self.__class__.__name__}')


class AAbstractUser(AbstractUser, AModel):
    """Enhanced abstract user model with service integration."""

    objects: ClassVar[AUserManager[Self]] = AUserManager()

    class Meta:
        abstract = True
