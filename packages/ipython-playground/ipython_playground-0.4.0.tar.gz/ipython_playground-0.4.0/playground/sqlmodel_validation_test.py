# with Session(get_engine()) as session:
# 	user = Doctor(clerk_id="hi")
# 	llm_response = LLMResponse(
# 		model="gpt-3.5-turbo",
# 		category="test",
# 		prompt="hello",
# 		response="world",
# 		prompt_hash="hi"
# 	)
# 	session.add(llm_response)
# 	session.add(user)
# 	session.commit()
# 	# session.close()

# llm_response = LLMResponse(
# 	model="gpt-3.5-turbo",
# 	category="test",
# 	prompt="hello from save",
# 	response="world",
# )
# llm_response.save()

# from activemodel import BaseModel as ActiveModelBaseModel
# from pydantic import validate_model

# # TODO this approach isn't great, it model_validate copies the entire model when successful
# class TestSQLModelValidationWithConstructor(ActiveModelBaseModel):
#     def __init__(self, **data) -> None:
#         super().__init__(**data)
#         _, _, validation_error = self.__class__.model_validate(self.__class__, data)
#         if validation_error:
#             raise validation_error

#     @model_validator(mode="before")
#     @classmethod
#     def before_validation(cls, data):
#          breakpoint()

# class TestValidationModel(BaseModel):
#     prompt: str
#     prompt_hash: str | None

#     @model_validator(mode="before")
#     @classmethod
#     def check_card_number_omitted(cls, data):
#         if isinstance(data, dict):
#             assert "card_number" not in data, "card_number should not be included"
#         return data

#     @field_validator("prompt_hash")
#     @classmethod
#     def prevent_explicit_hash(cls, v):
#         if v is not None:
#             raise ValueError("prompt_hash cannot be set explicitly")
#         return v

# # TestValidationModel(prompt="foo", prompt_hash="bar")