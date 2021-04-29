import frappe

from frappe import _
from frappe.utils.nestedset import get_root_of
from erpnext.selling.doctype.customer.customer import Customer

from typing import Dict


class EcommerceCustomer:
	def __init__(self, customer_id: str, customer_id_field: str, integration: str):
		self.customer_id = customer_id
		self.customer_id_field = customer_id_field
		self.integration = integration

	def is_synced(self) -> bool:
		"""Check if customer on Ecommerce site is synced with ERPNext"""

		return bool(frappe.db.exists("Customer", {self.customer_id_field: self.customer_id}))

	def get_customer_doc(self):
		"""Get ERPNext customer document."""
		if self.is_synced():
			doc: Customer = frappe.get_last_doc(
				"Customer", {self.customer_id_field: self.customer_id}
			)
			return doc
		else:
			raise frappe.DoesNotExistError()

	def sync_customer(self, customer_name: str, customer_group: str) -> None:
		"""Create customer in ERPNext if one does not exist already."""
		try:
			customer = frappe.get_doc(
				{
					"doctype": "Customer",
					"name": self.customer_id,
					self.customer_id_field: self.customer_id,
					"customer_name": customer_name,
					"customer_group": customer_group,
					"territory": get_root_of("Territory"),
					"customer_type": _("Individual"),
				}
			)

			customer.flags.ignore_mandatory = True
			customer.insert(ignore_permissions=True)

			frappe.db.commit()
		except Exception as e:
			raise e

	def create_customer_address(self, address: Dict[str, str]) -> None:
		"""Create address from dictionary containing fields used in Address doctype of ERPNext."""

		try:
			customer_doc = self.get_customer_doc()

			frappe.get_doc(
				{
					"doctype": "Address",
					**address,
					"links": [{"link_doctype": "Customer", "link_name": customer_doc.name}],
				}
			).insert(ignore_mandatory=True)

			frappe.db.commit()
		except Exception as e:
			raise e