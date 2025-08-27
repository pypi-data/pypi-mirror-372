# TODO not sure if this works
def patch_reload():
	# Store the original reload function
	_original_reload = importlib.reload

	def custom_reload(module):
		"""
		Custom reload function that wraps importlib.reload and resets
		SQLModel metadata after reloading the module.
		"""
		log.info("Clearing metadata before reload...")
		SQLModel.metadata.clear()

		result = _original_reload(module)
		return result

	# Replace the original reload with the custom one
	importlib.reload = custom_reload

patch_reload()
