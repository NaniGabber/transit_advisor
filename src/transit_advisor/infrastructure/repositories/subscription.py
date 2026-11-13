from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from transit_advisor.domain.exceptions import AlreadySubscribedError
from transit_advisor.domain.subscription import Subscription
from transit_advisor.infrastructure.database.models.subscription import (
    SubscriptionModel,
)


class SqlAlchemySubscriptionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, subscription: Subscription) -> Subscription:
        model = SubscriptionModel(
            user_id=subscription.user_id,
            route_id=subscription.route_id,
        )
        self._session.add(model)
        try:
            self._session.flush()
        except IntegrityError as exc:
            raise AlreadySubscribedError(
                subscription.user_id, subscription.route_id
            ) from exc
        return self._to_domain(model)

    def find_by_id(self, subscription_id: int) -> Subscription | None:
        model = self._session.get(SubscriptionModel, subscription_id)
        if model is None:
            return None
        return self._to_domain(model)

    def find_by_user_id(self, user_id: int) -> list[Subscription]:
        statement = select(SubscriptionModel).where(
            SubscriptionModel.user_id == user_id,
        )
        return [self._to_domain(m) for m in self._session.scalars(statement)]

    def find_by_route_id(self, route_id: int) -> list[Subscription]:
        statement = select(SubscriptionModel).where(
            SubscriptionModel.route_id == route_id,
        )
        return [self._to_domain(m) for m in self._session.scalars(statement)]

    def find_by_user_and_route(
        self,
        user_id: int,
        route_id: int,
    ) -> Subscription | None:
        statement = select(SubscriptionModel).where(
            SubscriptionModel.user_id == user_id,
            SubscriptionModel.route_id == route_id,
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return self._to_domain(model)

    def delete(self, subscription_id: int) -> None:
        self._session.execute(
            sa_delete(SubscriptionModel).where(
                SubscriptionModel.id == subscription_id,
            )
        )
        self._session.flush()

    def _to_domain(self, model: SubscriptionModel) -> Subscription:
        return Subscription(
            id=model.id,
            user_id=model.user_id,
            route_id=model.route_id,
        )
