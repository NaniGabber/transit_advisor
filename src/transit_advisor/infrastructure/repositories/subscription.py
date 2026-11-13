from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.subscription import (
    Subscription,
)
from transit_advisor.infrastructure.database.models.subscription import (
    SubscriptionModel,
)


class SqlAlchemySubscriptionRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(
        self,
        subscription: Subscription,
    ) -> Subscription:
        model = SubscriptionModel(
            user_id=subscription.user_id,
            route_id=subscription.route_id,
        )

        self._session.add(model)
        self._session.flush()

        return Subscription(
            id=model.id,
            user_id=model.user_id,
            route_id=model.route_id,
        )

    def find_by_user_id(
        self,
        user_id: int,
    ) -> list[Subscription]:
        statement = select(
            SubscriptionModel,
        ).where(
            SubscriptionModel.user_id == user_id,
        )

        models = self._session.scalars(
            statement,
        ).all()

        return [
            Subscription(
                id=model.id,
                user_id=model.user_id,
                route_id=model.route_id,
            )
            for model in models
        ]

    def find_by_route_id(
        self,
        route_id: int,
    ) -> list[Subscription]:
        statement = select(
            SubscriptionModel,
        ).where(
            SubscriptionModel.route_id == route_id,
        )

        models = self._session.scalars(
            statement,
        ).all()

        return [
            Subscription(
                id=model.id,
                user_id=model.user_id,
                route_id=model.route_id,
            )
            for model in models
        ]

    def find_by_user_and_route(
        self,
        user_id: int,
        route_id: int,
    ) -> Subscription | None:
        statement = select(
            SubscriptionModel,
        ).where(
            SubscriptionModel.user_id == user_id,
            SubscriptionModel.route_id == route_id,
        )

        model = self._session.scalar(
            statement,
        )

        if model is None:
            return None

        return Subscription(
            id=model.id,
            user_id=model.user_id,
            route_id=model.route_id,
        )
