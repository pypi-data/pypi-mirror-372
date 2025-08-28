from abc import ABC, ABCMeta, abstractmethod

from pinexq_client.core import NotAvailableException


class HypermediaAvailability(ABC):
	def __bool__(self) -> bool:
		return self.is_available()

	@staticmethod
	@abstractmethod
	def is_available() -> bool:
		...

class UnavailableAction(HypermediaAvailability):
	"""This class is used to represent an action that is not available. It is used to avoid None
	checks in the code."""

	def execute(self, *args, **kwargs):
		raise NotAvailableException(f"Error while executing action: action is not available")

	@staticmethod
	def is_available() -> bool:
		return False


class UnavailableLink(HypermediaAvailability):
	"""This class is used to represent a link that is not available. It is used to avoid None
	checks in the code."""

	def navigate(self):
		raise NotAvailableException(f"Error while navigating: link is not available")

	@staticmethod
	def is_available() -> bool:
		return False
