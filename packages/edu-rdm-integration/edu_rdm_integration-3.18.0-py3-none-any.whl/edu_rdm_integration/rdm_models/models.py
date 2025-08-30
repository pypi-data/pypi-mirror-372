from typing import (
    Optional,
    Type,
)

from django.db.models import (
    CASCADE,
    DateTimeField,
    ForeignKey,
    SmallIntegerField,
)
from m3.db import (
    BaseObjectModel,
)

from educommon.django.db.mixins import (
    ReprStrPreModelMixin,
)
from educommon.integration_entities.enums import (
    EntityLogOperation,
)
from educommon.utils.seqtools import (
    topological_sort,
)
from m3_db_utils.models import (
    FictiveForeignKeyField,
    ModelEnumValue,
    TitledModelEnum,
)


class BaseRDMModel(ReprStrPreModelMixin, BaseObjectModel):
    """Базовая модель РВД."""

    collecting_sub_stage = ForeignKey(
        verbose_name='Подэтап сбора данных',
        to='edu_rdm_integration_collect_data_stage.RDMCollectingDataSubStage',
        on_delete=CASCADE,
    )
    exporting_sub_stage = ForeignKey(
        verbose_name='Подэтап выгрузки данных',
        to='edu_rdm_integration_export_data_stage.RDMExportingDataSubStage',
        blank=True,
        null=True,
        on_delete=CASCADE,
    )
    operation = SmallIntegerField(
        verbose_name='Действие',
        choices=EntityLogOperation.get_choices(),
    )

    created = DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        null=True,
        blank=True,
        db_index=True,
    )
    modified = DateTimeField(
        verbose_name='Дата изменения',
        auto_now=True,
        null=True,
        blank=True,
        db_index=True,
    )

    @property
    def attrs_for_repr_str(self):
        """Список атрибутов для отображения экземпляра модели."""
        return ['collecting_sub_stage', 'exporting_sub_stage', 'operation', 'created', 'modified']

    class Meta:
        abstract = True


class RDMModelEnum(TitledModelEnum):
    """Модель-перечисление моделей "Региональная витрина данных"."""

    is_strict_order_number = True
    """Флаг, указывающий на уникальность порядкового номера элементов модели-перечисления."""

    class Meta:
        db_table = 'rdm_model'
        extensible = True
        verbose_name = 'Модель-перечисление моделей "Региональной витрины данных"'
        verbose_name_plural = 'Модели-перечисления моделей "Региональной витрины данных"'

    @classmethod
    def _get_model_dependencies(cls, model: Type[BaseRDMModel]) -> list[tuple[str, str]]:
        """Получение списка зависимостей модели РВД."""
        model_dependencies = []

        for field in model._meta.concrete_fields:
            if isinstance(field, FictiveForeignKeyField):
                model_dependencies.append(field.to)
            elif isinstance(field, ForeignKey):
                model_dependencies.append(field.related_model._meta.label)

        return model_dependencies

    @classmethod
    def _calculate_order_number(
        cls, order_number: Optional[int], model: Type[BaseRDMModel] = None, *args, **kwargs
    ) -> int:
        """Вычисление порядкового номера элемента модели-перечисления.

        Если order_number указан, то используется он.

        При добавлении новой модели РВД в модель-перечисление производится перерасчет порядковых номеров уже
        добавленных элементов. Порядок моделей РВД выстраивается по зависимости друг от друга. Зависимость определяется
        внешними ключами (ForeignKey) и фиктивными внешними ключами (FictiveForeignKey). Сначала идут модели не имеющие
        зависимостей, затем модели, которые зависят от других моделей. Сортировка моделей РВД происходит по алгоритму
        топологической сортировки.
        """
        if order_number is not None:
            return super()._calculate_order_number(order_number=order_number)

        enum_data = cls._get_enum_data()
        models = [model, *[model_enum_value.model for model_enum_value in enum_data.values()]]

        models_dependencies = []
        for model in models:
            model_dependencies = cls._get_model_dependencies(model=model)

            for model_dependency in model_dependencies:
                models_dependencies.append((model._meta.label, model_dependency))

        sorted_dependencies_models = topological_sort(models_dependencies)

        ordered_models = [*sorted_dependencies_models.cyclic, *reversed(sorted_dependencies_models.sorted)]

        for model_enum_value in enum_data.values():
            if model_enum_value.is_manual_order_number:
                try:
                    manual_index_model = ordered_models[model_enum_value.order_number - 1]
                except IndexError:
                    continue

                if manual_index_model != model_enum_value.model._meta.label and cls.is_strict_order_number:
                    raise ValueError(
                        f'Order number "{model_enum_value.order_number}" is already in use in the "{cls.__name__}". '
                        f'Please choose a different one.'
                    )
            else:
                model_enum_value.order_number = ordered_models.index(model_enum_value.model._meta.label) + 1

        return ordered_models.index(model._meta.label) + 1

    @classmethod
    def extend(
        cls,
        key,
        model: Type[BaseRDMModel] = None,
        title: str = '',
        creating_trigger_models: tuple = (),
        loggable_models: tuple = (),
        order_number: Optional[int] = None,
        *args,
        **kwargs,
    ):
        """Метод расширения модели-перечисления, например из плагина.

        Необходимо, чтобы сама модель-перечисление была расширяемой. Для этого необходимо, чтобы был установлен
        extensible = True в Meta.

        Args:
            key: ключ элемента перечисления, указывается заглавными буквами с разделителем нижнее подчеркивание
            title: название элемента перечисления
            model: модель, регистрируемая в модели-перечислении
            creating_trigger_models: модели продукта, которые инициируют создание записей модели РВД
            loggable_models: модели продукта, отслеживаемые в логах
            order_number: порядковый номер значения модели перечисления используемый при сортировке
            args: порядковые аргументы для модели-перечисления
            kwargs: именованные аргументы для модели-перечисления
        """
        if model is None:
            raise ValueError(f'Trying extend model "{cls.__name__}". Argument "model" is required.')

        is_manual_order_number = order_number is not None

        try:
            order_number = cls._calculate_order_number(
                order_number=order_number,
                model=model,
            )
        except ValueError as e:
            raise ValueError(f'Trying register model "{model.__name__}". {e.args[0]}')

        model_enum_value = ModelEnumValue(
            key=key,
            model=model,
            title=title,
            creating_trigger_models=creating_trigger_models,
            loggable_models=loggable_models,
            order_number=order_number,
            is_manual_order_number=is_manual_order_number,
            **kwargs,
        )

        setattr(cls, key, model_enum_value)
