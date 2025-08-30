"""Validators for DAPI."""

# pylint: disable=unused-import

from .activerecord import ActiveRecordDapiValidator
from .base import BaseDapiValidator, DapiValidator, ORMIntegration
from .dbt import DbtDapiValidator
from .fallback import FallbackDapiValidator
from .prisma import PrismaDapiValidator
from .protobuf import ProtobufDapiValidator
from .pynamodb import PynamodbDapiValidator
from .sequelize import SequelizeDapiValidator
from .sqlalchemy import SqlAlchemyDapiValidator
from .typeorm import TypeOrmDapiValidator

get_validator_for_integration = BaseDapiValidator.get_validator


ALWAYS_RUN_DAPI_VALIDATORS = {
    FallbackDapiValidator,
}
