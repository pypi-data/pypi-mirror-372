def iterate_on_model(model: SQLModel):
    from app.configuration.database import get_engine

    SQLModel.metadata.drop_all(
        tables=[SQLModel.metadata.tables[model.__tablename__]], bind=get_engine()
    )

    SQLModel.metadata.create_all(get_engine())
